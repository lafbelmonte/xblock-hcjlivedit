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
                alert("Something went wrong.");
            }
        });
    }

    function reset() {

        const resetCodeHandlerUrl = runtime.handlerUrl(element, "reset_code");

        $.ajax({
            type: "POST",
            url: resetCodeHandlerUrl,
            data: JSON.stringify({}),
            success: function (data) {
                update(data);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                alert("Something went wrong.");
            }
        });
    }

    function update({ htmlCode, cssCode, jsCode }) {
        htmlEditor.session.setValue(`${htmlCode}`);
        cssEditor.session.setValue(`${cssCode}`);
        jsEditor.session.setValue(`${jsCode}`);

        run();
    }

    function init(data) {
        htmlEditor.session.setMode("ace/mode/html");
        cssEditor.session.setMode("ace/mode/css");
        jsEditor.session.setMode("ace/mode/javascript");

        update(data);

        $("#html", element).keyup(run);
        $("#css", element).keyup(run);
        $("#js", element).keyup(run);
        $(".save", element).click(save);
        $(".reset", element).click(reset);
    }

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

    // $(function ($) {
    //     const loadCodeHandlerUrl = runtime.handlerUrl(element, "load_code");

    //     $.ajax({
    //         type: "POST",
    //         url: loadCodeHandlerUrl,
    //         data: JSON.stringify({}),
    //         success: init,
    //         error: function (jqXHR, textStatus, errorThrown) {
    //             console.log(errorThrown);
    //             $(".hcjlivedit_block", element).text("Something went wrong.");
    //         }
    //     });
    // });
}
