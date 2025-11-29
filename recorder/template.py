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
// 全局变量，设置循环播放次数
var LOOP_COUNT = 2;
var currentLoop = 0; // 当前循环次数

var _start= '{{start}}'
var _end= '{{end}}'
var _startPos = srt2sec(_start);
_startPos = _startPos ? _startPos : 0;
var _endPos = srt2sec(_end);
var _myAudio = document.querySelector('#myaudio');

// 用于存储 AudioContext 和 ScriptProcessorNode，确保只创建一次
var audioCtx = null;
var processor = null;
var source = null; // 添加 source 变量

function srt2sec(t) {
        // t='01:07:06,220'
        let t0= t.split(",")[0]
        let t1= t.split(",")[1]
        let a = t0.split(':');
        let seconds = parseInt(a[0]) * 60 * 60 + parseInt(a[1]) * 60 + parseInt(a[2])  +parseFloat('0.'+t1);
        return seconds
    }

// 这个函数只负责初始化 AudioContext 和事件监听一次
function init_audio_context(myAudio, startPos, endPos) {
    if (!audioCtx) { // 确保只创建一次 AudioContext
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        source = audioCtx.createMediaElementSource(myAudio);
        source.connect(audioCtx.destination);
        processor = audioCtx.createScriptProcessor(256, 1, 1);
        processor.connect(audioCtx.destination);
        processor.addEventListener('audioprocess', handleAudioProcess);
    }

    function handleAudioProcess() {
        // console.log('media current:', myAudio.currentTime, 'currentLoop:', currentLoop);

        // 如果当前播放时间超过结束位置
        if (myAudio.currentTime >= endPos) {
            // 首先判断是否已经达到或超过了预设的循环次数
            if (currentLoop >= LOOP_COUNT) {
                _pause(myAudio); // 达到循环次数后暂停
                myAudio.currentTime = startPos; // 暂停后将播放头移回起始位置
                currentLoop++; // 在这里将 currentLoop 递增，表示**已完成**所有循环
                return; // 停止进一步处理，不再进行下一次循环
            }
            // 如果未达到循环次数，则重置并增加循环计数
            myAudio.currentTime = startPos; // 重置到起始位置
            currentLoop++; // 增加循环计数
        }
    }
}

function _play(myAudio, startPos, endPos){
    // 每次点击播放，重置循环计数
    // 这里我们将 currentLoop 重置为 1,表示即将开始第一遍播放
    currentLoop = 1;

    // 确保 AudioContext 已初始化
    init_audio_context(myAudio, startPos, endPos);

    myAudio.currentTime = startPos; // 从头播放
    myAudio.play();
}

function _pause(myAudio){
    // 只有当音频正在播放中，或者音频已暂停但尚未完成所有循环时，才允许暂停/恢复
    if (!myAudio.paused || (myAudio.paused && currentLoop <= LOOP_COUNT)) {
        if (myAudio.paused) {
            myAudio.play();
        } else {
            myAudio.pause();
        }
    }
}


var userJs1 = ()=> {
   _play(_myAudio, _startPos, _endPos);
}

var userJs2 = ()=> {
   _pause(_myAudio);
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

// 进入页面后启动自动播放，并开始进入循环计数
_play(_myAudio,_startPos, _endPos);

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
