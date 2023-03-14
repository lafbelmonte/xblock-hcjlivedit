function HtmlCssJsLiveEditorEditXBlock(runtime, element) {
    window.RequireJS.require(["https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js"], function () {
        let editor;

        function save() {
            const saveInstructionHandler = runtime.handlerUrl(element, "save_instruction");

            $.ajax({
                type: "POST",
                url: saveInstructionHandler,
                data: JSON.stringify({ instruction: editor.getData() }),
                success: function (data) {
                    if (data.success) {
                        alert("Instruction saved successfully");
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

        ClassicEditor
            .create(document.querySelector("#instruction"))
            .then(function (newEditor) { editor = newEditor; })
            .catch(function (error) {
                console.log(error);
                $(".hcjlivedit_edit_block", element).text("Something went wrong.");
            });

        $(".save", element).click(save);
    });
}
