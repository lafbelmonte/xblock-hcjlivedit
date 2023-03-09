"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope

class HtmlCssJsLiveEditorXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    html_code = String(help="HTML code", default="<button>Click Me</button>", scope=Scope.user_state)
    css_code = String(help="CSS code", default="button { color: red; }", scope=Scope.user_state)
    js_code = String(help="JS code", default="document.querySelector(\"button\").addEventListener(\"click\", function() { alert(\"Good luck!\"); })", scope=Scope.user_state)


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the HtmlCssJsLiveEditorXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/hcjlivedit.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/hcjlivedit.css"))
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/ace/1.15.3/ace.min.js")
        frag.add_javascript(self.resource_string("static/js/src/hcjlivedit.js"))
        frag.initialize_js('HtmlCssJsLiveEditorXBlock')
        return frag

    @XBlock.json_handler
    def load_code(self, data, suffix=''):
        return { "htmlCode": self.html_code, "cssCode": self.css_code, "jsCode": self.js_code }
    
    @XBlock.json_handler
    def save_code(self, data, suffix=''):

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
        """A canned scenario for display in the workbench."""
        return [
            ("HtmlCssJsLiveEditorXBlock",
             """<hcjlivedit/>
             """),
            ("Multiple HtmlCssJsLiveEditorXBlock",
             """<vertical_demo>
                <hcjlivedit/>
                <hcjlivedit/>
                <hcjlivedit/>
                </vertical_demo>
             """),
        ]
