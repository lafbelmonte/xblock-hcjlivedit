import pkg_resources
import json
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Float, Scope, Boolean
from django.template import Context, Template
from xblockutils.studio_editable import StudioEditableXBlockMixin
from lms.djangoapps.courseware.models import StudentModule
from common.djangoapps.student.models import user_by_anonymous_id
from webob import Response
from submissions import api as submissions_api
from submissions.models import StudentItem as SubmissionsStudent


class HtmlCssJsLiveEditorXBlock(StudioEditableXBlockMixin, XBlock):

    has_author_view = True
    has_score = True

    display_name = String(
        default="HTML CSS JS Live Editor",
        display_name="Display Name",
        scope=Scope.settings
    )

    instruction = String(
        default="<p>Hello World!</p>",
        multiline_editor="html",
        resettable_editor=False,
        display_name="Instruction",
        help="Instruction students will see at the top of the code editor.",
        scope=Scope.settings
    )

    weight = Float(
        display_name="Maximum Score",
        help="Highest possible score a student could get.",
        default=1.0,
        scope=Scope.settings,
        values={"min": 0},
    )

    editable_fields = ("display_name", "instruction", "weight")

    default_html_code = String(default="", scope=Scope.settings)
    default_css_code = String(default="", scope=Scope.settings)
    default_js_code = String(default="", scope=Scope.settings)

    html_code = String(default=None, scope=Scope.user_state)
    css_code = String(default=None, scope=Scope.user_state)
    js_code = String(default=None, scope=Scope.user_state)

    has_submitted = Boolean(default=False, scope=Scope.user_state)
    comment = String(default=None, scope=Scope.user_state)

    def get_submission(self, student_id=None):
        submissions = submissions_api.get_submissions(
            self.get_student_item_dict(student_id)
        )
        if submissions:
            return submissions[0]

        return None

    def clear_student_state(self, *args, **kwargs):
        student_id = kwargs["user_id"]
        for submission in submissions_api.get_submissions(
            self.get_student_item_dict(student_id)
        ):
            submissions_api.reset_score(
                student_id, self.block_course_id(), self.block_id(), clear_state=True
            )

    def get_or_create_student_module(self, user):
        student_module, created = StudentModule.objects.get_or_create(
            course_id=self.course_id,
            module_state_key=self.location,
            student=user,
            defaults={
                "state": "{}",
                "module_type": self.category,
            },
        )

        return student_module

    def get_real_user(self):
        return self.runtime.get_real_user(self.xmodule_runtime.anonymous_student_id)

    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context={}):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def is_staff(self):
        return getattr(self.xmodule_runtime, "user_is_staff", False)

    def block_id(self):
        return str(self.scope_ids.usage_id)

    def score(self):
        return self.get_score()

    def block_course_id(self):
        return str(self.course_id)

    def get_score(self, student_id=None):
        score = submissions_api.get_score(
            self.get_student_item_dict(student_id))
        if score:
            return score["points_earned"]

        return None

    def get_student_module(self, module_id):
        return StudentModule.objects.get(pk=module_id)

    def get_student_item_dict(self, student_id=None):
        if student_id is None:
            student_id = self.xmodule_runtime.anonymous_student_id

        return {
            "student_id": student_id,
            "course_id": self.block_course_id(),
            "item_id": self.block_id(),
            "item_type": "hcjlivedit",
        }

    def student_view(self, context=None):

        context["is_staff"] = self.is_staff()
        context["instruction"] = self.instruction
        context["score"] = self.score()
        context["comment"] = self.comment
        context["weight"] = self.weight
        context["block_id"] = self.location.html_id()

        frag = Fragment()
        html = self.render_template("static/html/hcjlivedit.html", context)
        frag.add_content(html)
        frag.add_css(self.resource_string("static/css/hcjlivedit.css"))
        frag.add_javascript_url(
            self.runtime.local_resource_url(
                self, "public/js/vendor/ace-builds/src-min-noconflict/ace.js")
        )
        frag.add_css_url(
            self.runtime.local_resource_url(
                self, "public/js/vendor/datatables-builds/datatables/datatables.min.css")
        )
        frag.add_javascript_url(
            self.runtime.local_resource_url(
                self, "public/js/vendor/datatables-builds/datatables/datatables.min.js")
        )
        frag.add_javascript(self.resource_string(
            "static/js/src/hcjlivedit.js"))
        frag.initialize_js("HtmlCssJsLiveEditorXBlock", context["block_id"])
        return frag

    def author_view(self, context=None):

        context["block_id"] = self.location.html_id()
        context["instruction"] = self.instruction
        context["weight"] = self.weight

        frag = Fragment()
        html = self.render_template(
            "static/html/hcjlivedit_author.html", context)
        frag.add_content(html)

        return frag

    @XBlock.handler
    def reset_code(self, request, suffix=""):
        if self.has_submitted:
            return Response("You have already submitted, please wait for your score.", status_code=400)

        self.html_code = self.default_html_code
        self.css_code = self.default_css_code
        self.js_code = self.default_js_code

        return Response(json_body={"htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code})

    @XBlock.handler
    def load_code(self, request, suffix=""):
        if self.html_code is None:
            self.html_code = self.default_html_code

        if self.css_code is None:
            self.css_code = self.default_css_code

        if self.js_code is None:
            self.js_code = self.default_js_code

        return Response(json_body={"htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code})

    @XBlock.handler
    def save_code(self, request, suffix=""):

        if self.has_submitted:
            return Response("You have already submitted, please wait for your score.", status_code=400)

        html_code = request.POST["htmlCode"]
        css_code = request.POST["cssCode"]
        js_code = request.POST["jsCode"]

        if html_code is None:
            return Response("HTML code is required.", status_code=400)

        if css_code is None:
            return Response("CSS code is required.", status_code=400)

        if js_code is None:
            return Response("JS code is required.", status_code=400)

        self.html_code = html_code
        self.css_code = css_code
        self.js_code = js_code

        return Response(json_body={"message": "Code saved successfully."})

    @XBlock.handler
    def submit_score(self, request, suffix=""):

        if not self.is_staff():
            return Response("You can't access this resource.", status_code=403)

        score = request.POST["score"]
        comment = request.POST["comment"]
        module_id = request.POST["moduleId"]
        submission_id = request.POST["submissionId"]

        if score is None:
            return Response("Score is required.", status_code=400)

        if comment is None:
            return Response("Comment is required.", status_code=400)

        if module_id is None:
            return Response("Module ID is required.", status_code=400)

        if submission_id is None:
            return Response("Submission ID is required.", status_code=400)

        try:
            score = int(score)
        except ValueError:
            return Response("Score is invalid.", status_code=400)

        module = self.get_student_module(module_id)
        state = json.loads(module.state)

        submissions_api.set_score(submission_id, score, self.weight)

        state["comment"] = comment

        module.state = json.dumps(state)
        module.save()

        return Response(json_body={"message": "Score submitted successfully."})

    @XBlock.handler
    def remove_score(self, request, suffix=""):
        if not self.is_staff():
            return Response("You can't access this resource.", status_code=403)

        student_id = request.POST["studentId"]
        module_id = request.POST["moduleId"]

        if student_id is None:
            return Response("Student ID is required.", status_code=400)

        if module_id is None:
            return Response("Module ID is required.", status_code=400)

        submissions_api.reset_score(
            student_id, self.block_course_id(), self.block_id())

        module = self.get_student_module(module_id)
        state = json.loads(module.state)

        state["comment"] = None

        module.state = json.dumps(state)
        module.save()

        return Response(json_body={"message": "Score removed successfully."})

    @XBlock.handler
    def load_submissions(self, request, suffix=""):

        if not self.is_staff():
            return Response("You can't access this resource.", status_code=403)

        students = SubmissionsStudent.objects.filter(
            course_id=self.course_id, item_id=self.block_id()
        )

        def get_student_data():
            for student in students:
                submission = self.get_submission(student.student_id)
                if not submission:
                    continue
                user = user_by_anonymous_id(student.student_id)
                student_module = self.get_or_create_student_module(user)
                state = json.loads(student_module.state)
                score = self.get_score(student.student_id)
                yield {
                    "module_id": student_module.id,
                    "student_id": student.student_id,
                    "submission_id": submission["uuid"],
                    "username": student_module.student.username,
                    "fullname": student_module.student.profile.name,
                    "html_code": submission["answer"]["html_code"],
                    "css_code": submission["answer"]["css_code"],
                    "js_code": submission["answer"]["js_code"],
                    "score": score,
                    "comment": state.get("comment")
                }

        return Response(json_body={"submissions": list(get_student_data()), "weight": self.weight})

    @XBlock.handler
    def submit_code(self, request, suffix=""):

        if self.has_submitted:
            return Response("You have already submitted, please wait for your score.", status_code=400)

        html_code = request.POST["htmlCode"]
        css_code = request.POST["cssCode"]
        js_code = request.POST["jsCode"]

        if html_code is None:
            return Response("HTML code is required.", status_code=400)

        if css_code is None:
            return Response("CSS code is required.", status_code=400)

        if js_code is None:
            return Response("JS code is required.", status_code=400)

        self.html_code = html_code
        self.css_code = css_code
        self.js_code = js_code

        user = self.get_real_user()
        self.get_or_create_student_module(user)
        answer = {
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code
        }

        student_item_dict = self.get_student_item_dict()

        submissions_api.create_submission(student_item_dict, answer)

        self.has_submitted = True

        return Response(json_body={"message": "Code submitted successfully."})

    @staticmethod
    def workbench_scenarios():
        return [("HtmlCssJsLiveEditorXBlock", "<hcjlivedit/>")]
