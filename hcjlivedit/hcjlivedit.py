import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope
from django.template import Context, Template
from xblockutils.studio_editable import StudioEditableXBlockMixin

class HtmlCssJsLiveEditorXBlock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        default="HTML CSS JS Live Editor",
        display_name="Display Name"
    )

    has_author_view = True

    instruction = String(
        default="<p>Hello World!</p>", 
        multiline_editor="html", 
        resettable_editor=False,
        display_name="Instruction",
        help="Instruction students will see at the top of the code editor."
    )

    default_html_code = String(default="")
    default_css_code = String(default="")
    default_js_code = String(default="")

    html_code = String(default=None, scope=Scope.user_state)
    css_code = String(default=None, scope=Scope.user_state)
    js_code = String(default=None, scope=Scope.user_state)
    
    editable_fields = ("display_name", "instruction")

    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
    
    def render_template(self, template_path, context={}):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))
    
    def student_view(self, context=None):
        frag = Fragment()
        html = self.render_template("static/html/hcjlivedit.html", {"self": self, "context": context})
        frag.add_content(html)
        frag.add_css(self.resource_string("static/css/hcjlivedit.css"))
        frag.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/vendor/ace-builds/src-min-noconflict/ace.js")
        )
        frag.add_javascript(self.resource_string("static/js/src/hcjlivedit.js"))
        frag.initialize_js("HtmlCssJsLiveEditorXBlock")
        return frag
    
    def author_view(self, context=None):
        context["author"] = True
        return self.student_view(context)
    
    @XBlock.json_handler
    def save_instruction(self, data, suffix=""):

        success = True

        if data["instruction"] is None:
            success = False

        self.instruction = data["instruction"]

        return { "success": success }


    @XBlock.json_handler
    def reset_code(self, data, suffix=""):
        self.html_code = self.default_html_code
        self.css_code = self.default_css_code
        self.js_code = self.default_js_code

        return {"htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code }

    @XBlock.json_handler
    def load_code(self, data, suffix=""):

        if self.html_code is None:
            self.html_code = self.default_html_code
        
        if self.css_code is None:
            self.css_code = self.default_css_code

        if self.js_code is None:
            self.js_code = self.default_js_code

        return {"htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code }
    
    @XBlock.json_handler
    def save_code(self, data, suffix=""):

        success = True

        if data["htmlCode"] is None:
            success = False
        
        if data["cssCode"] is None:
            success = False

        if data["jsCode"] is None:
            success = False
        
        self.html_code = data["htmlCode"]
        self.css_code = data["cssCode"]
        self.js_code = data["jsCode"]

        return { "success": success }

    @staticmethod
    def workbench_scenarios():
        return [("HtmlCssJsLiveEditorXBlock", "<hcjlivedit/>")]
