# https://ankiweb.net/shared/info/952691989
front = """
{{audio}}
<br>
<div id="button_wrapper">
<button id="play" onclick="userJs1()">play</button>
<button id="pause" onclick="userJs2()">pause</button>
</div>
<script>

var _start= '{{start}}'
var _end= '{{end}}'
var _offset= '{{offset}}'
_offset= parseFloat(parseFloat(_offset)/1000)
var _startPos = srt2sec(_start);
_startPos = _startPos ? _startPos + _offset : 0;
var _endPos = srt2sec(_end) + _offset;
var _myAudio = document.querySelector('#myaudio');

function srt2sec(t) {
        // t='01:07:06,220'
        let t0= t.split(",")[0]
        let t1= t.split(",")[1]
        let a = t0.split(':');
        let seconds = parseInt(a[0]) * 60 * 60 + parseInt(a[1]) * 60 + parseInt(a[2])  +parseFloat('0.'+t1);
        return seconds
    }

function run_audio(myAudio,startPos, endPos){
    if (endPos) {
        myAudio.addEventListener('timeupdate', () => {
            if (myAudio.currentTime > endPos) {
                //myAudio.pause();
                myAudio.currentTime = startPos;
            }
        })
    } else {
        myAudio.addEventListener('ended', () => {
            myAudio.currentTime = startPos;
        })
    }
    myAudio.currentTime = startPos
    myAudio.play()
}

function _play(myAudio,startPos, endPos){
      myAudio.currentTime = startPos;
      myAudio.play();
    }

function _pause(myAudio, startPos, endPos){
    if (myAudio.paused) {
        myAudio.play();
    }
    else {
        myAudio.pause();
    }
}

var userJs1 = ()=> {
   _play(_myAudio, _startPos, _endPos)
}

var userJs2 = ()=> {
   _pause(_myAudio, _startPos, _endPos)
}

function throttle(fn, delay=200) {
  var isFinished = true;
  return function() {
      if (!isFinished) return;
      isFinished = false;
      var that = this, args = arguments;
      setTimeout(function() {
          fn.apply(that, args);
          isFinished = true;
      }, delay);
  };
}

window.onkeydown = throttle((e)=> {
        if (e.key == 'g') {
            _play(_myAudio, _startPos, _endPos)
        }
    })

window.addEventListener("gamepadconnected", function(e) {
  var gp = navigator.getGamepads()[e.gamepad.index];

  setInterval(throttle(()=>{
    var gp = navigator.getGamepads()[e.gamepad.index];
    if (gp.buttons[4].pressed){//L1
    }
    if (gp.buttons[5].pressed){//R1
        _play(_myAudio, _startPos, _endPos)
    }
  }), 100)
});

run_audio(_myAudio,_startPos, _endPos)

</script>
"""
back = """
{{FrontSide}}
<h1>{{sentence}}</h1>
<h1>{{meaning}}</h1>
"""
css = """
h1, h2{
    text-align: center;
}

#button_wrapper{
    text-align: center;
}

#button_wrapper button {
  font-size: 1.5rem;
  border-radius: 1.1rem;
  padding: 0.5rem 0.7rem;
  box-shadow: 3px 2px 4px rgba(0, 0, 0, 0.3);
  border: none;
  transition: color 1s ease-in-out;
}

#button_wrapper button:active {
  background: none;
  background-color: gray!important;
}
"""
