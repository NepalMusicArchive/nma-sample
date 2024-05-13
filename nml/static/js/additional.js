
  /* dynamic select of media / format in dropdowns*/
  var media_name_select = document.getElementById("media_name");
  var format_mame_select = document.getElementById("format_name");

  media_name_select.onchange = function () {

    media = media_name_select.value;
    $("#additional_audio").hide();
    $("#additional_publication").hide();

    fetch('/format/' + media).then(function (response) {
       <!-- alert("test .. " + media);  -->
       if ($("#media_name").val() == "1" || $("#media_name").val() == "2") {
        $("#additional_media").show();
      } else {
        $("#additional_media").hide();

      }
      response.json().then(function (data) {
        var optionHTML = '';

        for (var format_mame_select of data.format_list) {
          optionHTML += '<option value="' + format_mame_select.id + '">' + format_mame_select.name + '</option>';
        }

        format_name.innerHTML = optionHTML;
      })

    });
  }

  $(document).ready(function () {


    $("#open").click(function () {
      $.ajax({
        url: '/record_company',
        type: 'GET',
        success: function (response) {
          $("#target-div").html(response);
        }
      });
    });

    


    /* select additional div on page load */
    /* if format is cd , album cover, vinyl or cassette */
    if ($("#format_name").val() == "1" || $("#format_name").val() == "10" || $("#format_name").val() == "12" || $("#format_name").val() == "14" || $("#format_name").val() == "3") {
      $("#additional_audio").show();
      $("#additional_publication").hide();
    } else if ($("#format_name").val() == "8") { /* if format is publication*/
      $("#additional_audio").hide();
      $("#additional_publication").show();
    } else {
      $("#additional_audio").hide();
      $("#additional_publication").hide();
    }

    /* select additional div on dropdown change */
    $("#format_name").change(function () {
      console.log($(this).val())
      /* if format is cd , album cover, vinyl or cassette */
      if ($(this).val() == "1" || $(this).val() == "10" || $(this).val() == "12" || $(this).val() == "14" || $(this).val() == "3") {
        $("#additional_audio").show();
        $("#additional_publication").hide();
      } else if ($(this).val() == "8") { /* if format is publication*/
        $("#additional_audio").hide();
        $("#additional_publication").show();

      } else {
        $("#additional_audio").hide();
        $("#additional_publication").hide();
      }

    });

  });
