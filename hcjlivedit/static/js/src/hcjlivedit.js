/* Javascript for HtmlCssJsLiveEditorXBlock. */
function HtmlCssJsLiveEditorXBlock(runtime, element) {

    let htmlEditor = ace.edit("html");
    let cssEditor = ace.edit("css");
    let jsEditor = ace.edit("js");

    function run() {
        let htmlCode = htmlEditor.getValue();
        let cssCode = "<style>" + cssEditor.getValue() + "</style>";
        let jsCode = jsEditor.getValue();
        let page = document.querySelector("#page");

        page.contentDocument.body.innerHTML = htmlCode + cssCode;
        page.contentWindow.eval(jsCode);
    }


    $(function ($) {
        /* Here's where you'd do things on page load. */

        htmlEditor.session.setMode("ace/mode/html");
        cssEditor.session.setMode("ace/mode/css");
        jsEditor.session.setMode("ace/mode/javascript");

        document.querySelector("#html").addEventListener("keyup", run);
        document.querySelector("#css").addEventListener("keyup", run);
        document.querySelector("#js").addEventListener("keyup", run);

    });
}
