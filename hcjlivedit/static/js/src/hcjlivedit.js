function HtmlCssJsLiveEditorXBlock(runtime, element) {
    let htmlEditor = ace.edit("html");
    let cssEditor = ace.edit("css");
    let jsEditor = ace.edit("js");
  
    let datatable;
  
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
        data: {
          htmlCode,
          cssCode,
          jsCode,
        },
        success: function (data) {
          alert(data.message);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          alert(jqXHR.responseText);
        },
      });
    }
  
    function reset() {
      const resetCodeHandlerUrl = runtime.handlerUrl(element, "reset_code");
  
      $.ajax({
        type: "POST",
        url: resetCodeHandlerUrl,
        success: function (data) {
          update(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          alert(jqXHR.responseText);
        },
      });
    }
  
    function submit() {
      if (
        confirm(
          "You will no longer be able to update your submission once you submit. Confirm?"
        ) == true
      ) {
        const submitCodeHandlerUrl = runtime.handlerUrl(element, "submit_code");
  
        let htmlCode = htmlEditor.getValue();
        let cssCode = cssEditor.getValue();
        let jsCode = jsEditor.getValue();
  
        $.ajax({
          type: "POST",
          url: submitCodeHandlerUrl,
          data: {
            htmlCode,
            cssCode,
            jsCode,
          },
          success: function (data) {
            alert(data.message);
          },
          error: function (jqXHR, textStatus, errorThrown) {
            alert(jqXHR.responseText);
          },
        });
      }
    }
  
    function loadSubmissions() {
      if ($("#submissions_div", element).css("display") === "none") {
        const loadSubmissionsHandlerUrl = runtime.handlerUrl(
          element,
          "load_submissions"
        );
  
        $.ajax({
          type: "GET",
          url: loadSubmissionsHandlerUrl,
          success: function (data) {
            datatable.clear();
            datatable.rows.add(data.submissions);
            datatable.draw();
  
            $("#submissions_div", element).css("display", "block");
          },
          error: function (jqXHR, textStatus, errorThrown) {
            $("#submissions_div", element).text("Something went wrong.");
          },
        });
      } else {
        $("#submissions_div", element).css("display", "none");
      }
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
      $("#save", element).click(save);
      $("#reset", element).click(reset);
      $("#submit", element).click(submit);
      $("#submissions", element).click(loadSubmissions);
  
      datatable = $("#submissions_table").DataTable({
        info: false,
        autoWidth: false,
        columns: [
          {
            data: "submission_id",
          },
          {
            data: "username",
          },
          {
            data: "fullname",
          },
          {
            data: "html_code",
          },
          {
            data: "css_code",
          },
          {
            data: "js_code",
          },
        ],
        columnDefs: [
          {
            target: 0,
            visible: false,
            searchable: false,
          },
          {
            target: 3,
            visible: false,
            searchable: false,
          },
          {
            target: 4,
            visible: false,
            searchable: false,
          },
          {
            target: 5,
            visible: false,
            searchable: false,
          },
        ],
      });
  
      $("#submissions_table tbody").on("click", "tr", function () {
        var data = datatable.row(this).data();
        update({
          htmlCode: data.html_code,
          cssCode: data.css_code,
          jsCode: data.js_code,
        });
      });
    }
  
    const loadCodeHandlerUrl = runtime.handlerUrl(element, "load_code");
  
    $.ajax({
      type: "GET",
      url: loadCodeHandlerUrl,
      success: init,
      error: function (jqXHR, textStatus, errorThrown) {
        $(".hcjlivedit_block", element).text("Something went wrong.");
      },
    });
  }
  