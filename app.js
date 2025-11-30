(function(){
  const CHARACTERS = {
    '1': ["Cat","🐱","Meow! I hide numbers inside yarn balls."],
    '2': ["Robot","🤖","Beep! I compute a secret integer."],
    '3': ["Panda","🐼","Nom nom... I thought of a bamboo-number."],
    '4': ["Dino","🦖","Roar! Try not to be eaten by wrong guesses."]
  };
  const LEVELS = {
    '1':["Easy",10,6],
    '2':["Medium",50,7],
    '3':["Hard",100,9]
  };
  const LeaderKey = 'cartoon_guess_leaderboard_v1';

  // Elements
  const el = id => document.getElementById(id);
  const playerName = el('playerName');
  const charSel = el('characterSel');
  const levelSel = el('levelSel');
  const startBtn = el('startBtn');
  const hintBtn = el('hintBtn');
  const tryBtn = el('tryBtn');
  const guessInput = el('guessInput');
  const speech = el('speech');
  const meta = el('meta');
  const log = el('log');
  const leaderList = el('leaderList');
  const clearBoard = el('clearBoard');

  let secret = 0, limit=10, attemptsLeft=0, hintsUsed=0, score=0, startTime=0;

  function loadLeaderboard(){
    try{
      const raw = localStorage.getItem(LeaderKey);
      return raw ? JSON.parse(raw) : [];
    }catch(e){return []}
  }
  function saveLeaderboard(arr){
    try{ localStorage.setItem(LeaderKey, JSON.stringify(arr)); }catch(e){}
  }
  function addScore(name,scoreVal,timeTaken){
    const table = loadLeaderboard();
    table.push({name,score:scoreVal,time:timeTaken,when:new Date().toISOString()});
    table.sort((a,b)=> b.score - a.score || a.time - b.time);
    saveLeaderboard(table.slice(0,50));
    renderLeaderboard();
  }

  function renderLeaderboard(){
    const table = loadLeaderboard();
    leaderList.innerHTML = '';
    if(table.length===0){ leaderList.innerHTML = '<li>(empty)</li>'; return }
    table.slice(0,10).forEach(e=>{
      const li = document.createElement('li');
      li.textContent = `${e.name} — ${e.score} pts`;
      leaderList.appendChild(li);
    });
  }

  function playSound(key){
    // Attempt to play sound from ../assets/sounds/<key>.wav
    try{
      const path = `../assets/sounds/${key}.wav`;
      const audio = new Audio(path);
      audio.play().catch(()=>{});
    }catch(e){}
  }

  function setMeta(){
    meta.textContent = `Hints: ${Math.max(0,3-hintsUsed)} \u00A0 Attempts: ${attemptsLeft} \u00A0 Score: ${score}`;
  }

  function startRound(){
    const name = (playerName.value || 'Player').trim();
    const levelIdx = levelSel.value;
    const charIdx = charSel.value;
    const level = LEVELS[levelIdx];
    limit = level[1];
    attemptsLeft = level[2];
    hintsUsed = 0;
    score = 100 + ((3 - parseInt(levelIdx)) * 10);
    secret = Math.floor(Math.random()*limit)+1;
    startTime = Date.now();
    speech.innerHTML = `${CHARACTERS[charIdx][1]} <strong>${CHARACTERS[charIdx][0]}</strong> — Guess a number between 1 and ${limit}`;
    log.innerHTML = `Round started for <strong>${name}</strong>. Good luck!`;
    setMeta();
    playSound('start');
    guessInput.focus();
  }

  function giveHint(){
    if(hintsUsed >= 3){ log.innerHTML = 'No hints left.'; return }
    const t = hintsUsed % 3;
    let hintText = '';
    if(t===0){
      const spread = Math.max(1, Math.floor(limit * 0.12));
      const low = Math.max(1, secret - spread);
      const high = Math.min(limit, secret + spread);
      hintText = `It's between ${low} and ${high}.`;
    }else if(t===1){
      if(secret % 5 === 0) hintText = "It's divisible by 5.";
      else if(secret % 2 === 0) hintText = "It's even.";
      else hintText = "It's odd.";
    }else{
      const low = Math.max(1, secret - 5);
      const high = Math.min(limit, secret + 5);
      hintText = `It's within ${low} and ${high}.`;
    }
    hintsUsed +=1;
    score = Math.max(0, score - 8);
    log.innerHTML = `💡 Hint: ${hintText}`;
    setMeta();
    playSound('hint');
  }

  function tryGuess(){
    const val = guessInput.value;
    if(!val){ log.innerHTML = 'Enter a guess!'; return }
    const g = parseInt(val,10);
    if(isNaN(g)){ log.innerHTML = 'Invalid number.'; return }

    if(g === secret){
      const elapsed = Math.floor((Date.now()-startTime)/1000);
      const bonus = Math.max(10, 60 - elapsed);
      const finalScore = Math.max(0, score + bonus);
      log.innerHTML = `🎉 Correct! You found it in ${elapsed}s. Score: ${finalScore} (+${bonus} speed bonus)`;
      playSound('win');
      addScore((playerName.value||'Player').trim(), finalScore, elapsed);
      // freeze round
      attemptsLeft = 0;
      setMeta();
      return;
    }

    if(g < secret){
      log.innerHTML = '⬆️ Too low!';
      playSound('pop');
    }else{
      log.innerHTML = '⬇️ Too high!';
      playSound('pop');
    }
    attemptsLeft -= 1;
    score = Math.max(0, score - 10);
    setMeta();

    if(attemptsLeft <= 0){
      log.innerHTML = `💥 Out of attempts! The number was ${secret}.`;
      playSound('lose');
      addScore((playerName.value||'Player').trim(), 0, Math.floor((Date.now()-startTime)/1000));
    }
  }

  startBtn.addEventListener('click', startRound);
  hintBtn.addEventListener('click', giveHint);
  tryBtn.addEventListener('click', tryGuess);
  guessInput.addEventListener('keydown', e => { if(e.key === 'Enter') tryGuess(); });
  clearBoard.addEventListener('click', ()=>{ localStorage.removeItem(LeaderKey); renderLeaderboard(); });

  // init
  renderLeaderboard();
  setMeta();
})();
