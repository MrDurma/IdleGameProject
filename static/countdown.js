// TODO: For now timer works only for first building, implement timer so it works for each busy building.
function countdown(endTime, elementId) {
    let hours, minutes, seconds;
    // let endTime = document.getElementById("end_time").value;
    let end = new Date();
    let endHours = endTime.split(':')[0];
    let endMinutes = endTime.split(':')[1];
    let endSeconds = endTime.split(':')[2];

    // Calling subtraction function every 1000ms (1 second)
    setInterval(subtraction, 1000);
  
    function subtraction() {
      document.getElementById("testing"/*elementId + "_timer"*/).innerHTML = endHours + ":" + endMinutes + ":" + endSeconds;
      endSeconds--;
      if (endSeconds <= 0 ) {
        if (endHours > 0 && endMinutes == 0){
          endHours--;
          endMinutes == 59;
        }
        else if(endHours == 0 && endMinutes == 0){
          return;
        }
        endSeconds = 59;
        endMinutes--;
      }
    }
  }
  