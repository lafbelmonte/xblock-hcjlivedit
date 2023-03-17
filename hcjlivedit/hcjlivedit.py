import pkg_resources
import logging
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
from enum import Enum

log = logging.getLogger(__name__)

class HtmlCssJsLiveEditorXBlock(StudioEditableXBlockMixin, XBlock):

    Status = Enum("Status", "IN_PROGRESS SUBMITTED GRADED")

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

    status = String(default=Status.IN_PROGRESS.name, scope=Scope.user_state)


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
        if created:
            log.info(
                "Created student module %s [course: %s] [student: %s]",
                student_module.module_state_key,
                student_module.course_id,
                student_module.student.username,
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

    def block_course_id(self):
        return str(self.course_id)
    
    def get_score(self, student_id=None):
        score = submissions_api.get_score(self.get_student_item_dict(student_id))
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

        frag = Fragment()
        html = self.render_template("static/html/hcjlivedit.html", {"self": self, "context": context})
        frag.add_content(html)
        frag.add_css(self.resource_string("static/css/hcjlivedit.css"))
        frag.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/vendor/ace-builds/src-min-noconflict/ace.js")
        )
        frag.add_css_url(
            self.runtime.local_resource_url(self, "public/js/vendor/datatables-builds/datatables/datatables.min.css")
        )
        frag.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/vendor/datatables-builds/datatables/datatables.min.js")
        )
        frag.add_javascript(self.resource_string("static/js/src/hcjlivedit.js"))
        frag.initialize_js("HtmlCssJsLiveEditorXBlock")
        return frag
    
    def author_view(self, context=None):
        context["is_cms"] = True
        return self.student_view(context)
    
    @XBlock.handler
    def reset_code(self, request, suffix=""):

        if self.status is not self.Status.IN_PROGRESS.name:
            return Response("You have already submitted, please wait for your score.", status_code=400)

        self.html_code = self.default_html_code
        self.css_code = self.default_css_code
        self.js_code = self.default_js_code

        return Response(json_body={ "htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code })

    @XBlock.handler
    def load_code(self, request, suffix=""):

        if self.html_code is None:
            self.html_code = self.default_html_code
        
        if self.css_code is None:
            self.css_code = self.default_css_code

        if self.js_code is None:
            self.js_code = self.default_js_code

        return Response(json_body={ "htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code })
    
    @XBlock.handler
    def save_code(self, request, suffix=""):

        if self.status is not self.Status.IN_PROGRESS.name:
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

        return Response(json_body={ "message": "Code saved successfully." })
    
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
                    "js_code": submission["answer"]["css_code"],
                }

        return Response(json_body={ "submissions": list(get_student_data()) })

    @XBlock.handler
    def submit_code(self, request, suffix=""):

        if self.status is not self.Status.IN_PROGRESS.name:
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

        self.status = self.Status.SUBMITTED.name
        
        return Response(json_body={ "message": "Code submitted successfully." })

    @staticmethod
    def workbench_scenarios():
        return [("HtmlCssJsLiveEditorXBlock", "<hcjlivedit/>")]
