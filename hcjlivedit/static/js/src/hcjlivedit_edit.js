function HtmlCssJsLiveEditorEditXBlock(runtime, element) {

    function init(data) {
        ClassicEditor.instances['#instruction'].setData(data.instruction);
    }

    $(function ($) {
        ClassicEditor
            .create(document.querySelector("#instruction"))
            .catch((error) => console.log(error));

        const loadContentHandlerUrl = runtime.handlerUrl(element, "load_content");

        $.ajax({
            type: "POST",
            url: loadContentHandlerUrl,
            data: JSON.stringify({}),
            success: init,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                $(".hcjlivedit_edit_block", element).text("Something went wrong.");
            }
        });
    });
}
