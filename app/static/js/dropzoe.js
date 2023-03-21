let myDropzone = new Dropzone("#my-dropzone", {
  url: uploadUrl,
  // paramName: "image",
  maxFiles: 1,
  maxFilesize: 10,
  acceptedFiles: "image/*",
  addRemoveLinks: true,
  dictRemoveFile: "Remove",
  dictCancelUpload: 'Cancel', // text for cancel upload link
  dictDefaultMessage: 'Drop files here or click to upload', // default message
  autoProcessQueue: false,
  init: function () {
    var submitButton = document.querySelector("#submit-all");
    var myDropzone = this;

    submitButton.addEventListener("click", function () {
      // add textfield input to FormData object
      let textFieldValue = document.getElementById("post").value.trim();

      // Check if the text field is empty
      if (textFieldValue === "") {
        // If the text field is empty, display an error message and return
          const errorMessage = "Please enter some message";
          const errorSpan = document.getElementById("error");
          errorSpan.textContent = errorMessage;
        return;
      }
      let formData = new FormData();
      formData.append("textfield", document.getElementById("post").value);
      if (myDropzone.files.length > 0) {
        formData.append('image', myDropzone.files[0], myDropzone.files[0].name);
      }



      // submit the form data
      $.ajax({
        type: "POST",
        url: uploadUrl,
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          console.log(response);
          window.location.reload();

        },
        error: function(xhr, status, error) {
          console.log(error);
        }
      });
    });
  }
});
