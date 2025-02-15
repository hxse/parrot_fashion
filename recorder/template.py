# https://ankiweb.net/shared/info/952691989
"""
前端如何实现音频片段的的无误差毫秒级精准播放概述 本文会讲述 Web Audio API 以及音频剪切等几种实现精准控制 - 掘金
https://juejin.cn/post/7343534050149482536
https://telegra.ph/%E5%89%8D%E7%AB%AF%E5%A6%82%E4%BD%95%E5%AE%9E%E7%8E%B0%E9%9F%B3%E9%A2%91%E7%89%87%E6%AE%B5%E7%9A%84%E7%9A%84%E6%97%A0%E8%AF%AF%E5%B7%AE%E6%AF%AB%E7%A7%92%E7%BA%A7%E7%B2%BE%E5%87%86%E6%92%AD%E6%94%BE-02-15-2
"""
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
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaElementSource(myAudio);
    source.connect(audioCtx.destination);
    const processor = audioCtx.createScriptProcessor(256);
    processor.connect(audioCtx.destination);
    processor.addEventListener('audioprocess', handleAudioProcess);

    function handleAudioProcess(){
        console.log('media current:', myAudio.currentTime);
        if (myAudio.currentTime > endPos) {
            myAudio.currentTime = startPos;
        }
    }
    _play(myAudio,startPos, endPos)
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
