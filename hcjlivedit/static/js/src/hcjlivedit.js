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

    function save() {

        const saveCodeHandlerUrl = runtime.handlerUrl(element, "save_code");

        let htmlCode = htmlEditor.getValue();
        let cssCode = cssEditor.getValue();
        let jsCode = jsEditor.getValue();

        $.ajax({
            type: "POST",
            url: saveCodeHandlerUrl,
            data: JSON.stringify({ htmlCode, cssCode, jsCode }),
            success: function (data) {
                if (data.success) {
                    alert("Code saved successfully");
                } else {
                    alert("Something went wrong.");
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                alert("Something went wrong.")
            }
        });
    }

    function init(data) {
        htmlEditor.session.setMode("ace/mode/html");
        cssEditor.session.setMode("ace/mode/css");
        jsEditor.session.setMode("ace/mode/javascript");

        htmlEditor.session.setValue(`${data.htmlCode}`);
        cssEditor.session.setValue(`${data.cssCode}`);
        jsEditor.session.setValue(`${data.jsCode}`);

        run();

        $("#html", element).keyup(run);
        $("#css", element).keyup(run);
        $("#js", element).keyup(run);
        $(".save", element).click(save);
    }

    $(function ($) {
        const loadCodeHandlerUrl = runtime.handlerUrl(element, "load_code");

        $.ajax({
            type: "POST",
            url: loadCodeHandlerUrl,
            data: JSON.stringify({}),
            success: init,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                $(".hcjlivedit_block", element).text("Something went wrong.");
            }
        });
    });
}
