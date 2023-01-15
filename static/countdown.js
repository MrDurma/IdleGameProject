/* This function takes parameters timeLeft(supports only hh:mm:ss format) 
and elementId(id of element where to display time */
function countdown(timeLeft, elementId) {
    // Initialising variables
    let hoursLeft = timeLeft.split(':')[0];
    let minutesLeft = timeLeft.split(':')[1];
    let secondsLeft = timeLeft.split(':')[2];

    // Calling subtraction function every 1000ms (1 second)
    let intervalId = setInterval(subtraction, 1000);
    
    // This function is subtracting time (one second) on each iteration.
    function subtraction() {
      // Displaying changes on website in hh:mm:ss format.
      document.getElementById(elementId + "_timer").innerHTML = "Time left: " + 
                              `0${hoursLeft}`.slice(-2) + ":" + `0${minutesLeft}`.slice(-2) + 
                              ":" + `0${secondsLeft}`.slice(-2);
      if (secondsLeft == 0){
        if (minutesLeft == 0){
          if (hoursLeft == 0) {
            location.reload()
            setTimeout(function() {
              clearInterval(intervalId);
            }, 1000);
              
          }
          else {
            hoursLeft--;
            minutesLeft = 59;
            secondsLeft = 60;
          }
        }
        else {
          minutesLeft--;
          secondsLeft = 60;
        }
      }
      secondsLeft--;
    }
  }
  