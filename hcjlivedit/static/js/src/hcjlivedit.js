function HtmlCssJsLiveEditorXBlock(runtime, element, { block_id }) {
  let htmlEditor = ace.edit("html-editor");
  let cssEditor = ace.edit("css-editor");
  let jsEditor = ace.edit("js-editor");

  let datatable;

  let selectedRow = null;

  function run() {
    let htmlCode = htmlEditor.getValue();
    let cssCode = "<style>" + cssEditor.getValue() + "</style>";
    let jsCode = jsEditor.getValue();
    let codeOutput = document.querySelector("#code-output");

    codeOutput.contentDocument.body.innerHTML = htmlCode + cssCode;
    codeOutput.contentWindow.eval(jsCode);
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
        console.log(jqXHR.responseText);
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
        console.log(jqXHR.responseText);
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
          console.log(jqXHR.responseText);
          alert(jqXHR.responseText);
        },
      });
    }
  }

  function updateDataTable(data) {
    datatable.clear();
    datatable.rows.add(data);
    datatable.draw();
  }

  function loadSubmissions() {
    if ($("#submissions-area", element).css("display") === "none") {
      const loadSubmissionsHandlerUrl = runtime.handlerUrl(
        element,
        "load_submissions"
      );

      $.ajax({
        type: "GET",
        url: loadSubmissionsHandlerUrl,
        success: function (data) {
          updateDataTable(
            data.submissions.map(function (item) {
              return { weight: data.weight, ...item };
            })
          );
          $("#submissions-area", element).css("display", "block");
        },
        error: function (jqXHR, textStatus, errorThrown) {
          console.log(jqXHR.responseText);
          $("#submissions-area", element).text(
            "Something went wrong, please check the console."
          );
        },
      });
    } else {
      $("#submissions-table tbody tr").removeClass("row-selected");
      update({
        htmlCode: "",
        cssCode: "",
        jsCode: "",
      });
      selectedRow = null;
      $("#submissions-area", element).css("display", "none");
    }
  }

  function update({ htmlCode, cssCode, jsCode }) {
    htmlEditor.session.setValue(`${htmlCode}`);
    cssEditor.session.setValue(`${cssCode}`);
    jsEditor.session.setValue(`${jsCode}`);

    run();
  }

  function submitScore(e) {
    e.preventDefault();

    const submitScoreHandlerUrl = runtime.handlerUrl(element, "submit_score");

    let score = $("#score", element).val();
    let comment = $("#comment", element).val();

    let candidateData = datatable
      .data()
      .toArray()
      .map(function (item) {
        if (selectedRow.submission_id === item.submission_id) {
          return {
            ...item,
            score,
            comment,
          };
        }

        return item;
      });

    $.ajax({
      type: "POST",
      url: submitScoreHandlerUrl,
      data: {
        score,
        comment,
        moduleId: selectedRow.module_id,
        submissionId: selectedRow.submission_id,
      },
      success: function (data) {
        updateDataTable(candidateData);
        alert(data.message);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log(jqXHR.responseText);
        alert(jqXHR.responseText);
      },
    });
  }

  function openSubmitScoreModal() {
    if (selectedRow) {
      $("#score", element).attr({
        min: 0,
        max: selectedRow.weight,
      });
      $("#score", element).val(selectedRow.score);
      $("#comment", element).val(selectedRow.comment);
      $("#submit-score-modal-title", element).text(
        `Scoring ${selectedRow.fullname}, maximum score is ${selectedRow.weight}.`
      );
      $("#submit-score-modal", element).css("display", "block");
    }
  }

  function closeSubmitScoreModal() {
    $("#submit-score-modal-title", element).text("");
    $("#score", element).val(null);
    $("#comment", element).val(null);
    $("#submit-score-modal", element).css("display", "none");
  }

  function removeScore() {
    if (selectedRow) {
      let candidateData = datatable
        .data()
        .toArray()
        .map(function (item) {
          if (selectedRow.submission_id === item.submission_id) {
            return {
              ...item,
              score: null,
              comment: null,
            };
          }

          return item;
        });

      if (
        confirm(
          `This will remove the score of ${selectedRow.fullname}. Confirm?`
        ) == true
      ) {
        const removeScoreHandler = runtime.handlerUrl(element, "remove_score");

        $.ajax({
          type: "POST",
          url: removeScoreHandler,
          data: {
            moduleId: selectedRow.module_id,
            studentId: selectedRow.student_id,
          },
          success: function (data) {
            updateDataTable(candidateData);
            alert(data.message);
          },
          error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.responseText);
            alert(jqXHR.responseText);
          },
        });
      }
    }
  }

  function init(data) {
    htmlEditor.session.setMode("ace/mode/html");
    cssEditor.session.setMode("ace/mode/css");
    jsEditor.session.setMode("ace/mode/javascript");

    update(data);

    $("#html-editor", element).keyup(run);
    $("#css-editor", element).keyup(run);
    $("#js-editor", element).keyup(run);
    $("#save-button", element).click(save);
    $("#reset-button", element).click(reset);
    $("#submit-button", element).click(submit);
    $("#submissions-button", element).click(loadSubmissions);
    $("#remove-score-button", element).click(removeScore);
    $("#open-submit-score-modal-button", element).click(openSubmitScoreModal);
    $("#close-submit-score-modal-button", element).click(closeSubmitScoreModal);
    $("#submit-score-form", element).submit(submitScore);

    datatable = $("#submissions-table").DataTable({
      info: false,
      autoWidth: false,
      select: true,
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
          data: "score",
          render: function (data, type, row) {
            if (type === "display") {
              if (!data) {
                return "N/A";
              }

              return `${data} / ${row.weight}`;
            }

            return data;
          },
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
          target: 4,
          visible: false,
          searchable: false,
        },
        {
          target: 5,
          visible: false,
          searchable: false,
        },
        {
          target: 6,
          visible: false,
          searchable: false,
        },
      ],
    });

    $("#submissions-table tbody").on("click", "tr", function () {
      $("#submissions-table tbody tr").removeClass("row-selected");
      const data = datatable.row(this).data();

      selectedRow = data;

      update({
        htmlCode: data.html_code,
        cssCode: data.css_code,
        jsCode: data.js_code,
      });
      $(this).addClass("row-selected");
    });
  }

  const loadCodeHandlerUrl = runtime.handlerUrl(element, "load_code");

  $.ajax({
    type: "GET",
    url: loadCodeHandlerUrl,
    success: init,
    error: function (jqXHR, textStatus, errorThrown) {
      console.log(jqXHR.responseText);
      $("#hcjle-block", element).text(
        "Something went wrong, please check the console."
      );
    },
  });
}
