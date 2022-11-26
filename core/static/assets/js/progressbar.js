// ------------ Progress bar -------------------- //

function progress(timeleft, timetotal, $element) {
    var progressBarWidth = timeleft * $element.width() / timetotal;
    $element.find('.bar').animate({
      width: progressBarWidth
    }, 900);
  };