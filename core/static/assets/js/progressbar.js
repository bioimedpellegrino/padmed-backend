// ------------ Progress bar -------------------- //

function progress(current, total, $element) {
    var progressBarWidth = current * $element.width() / total;
    if (progressBarWidth === 0){
      progressBarWidth = total * 0.15;
    }
    $element.find('.bar').animate({
      width: progressBarWidth
    }, 900);
  };