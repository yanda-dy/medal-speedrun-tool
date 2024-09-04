let processedIds = new Set();

// Function to fetch and process the play history
function fetchAndProcessPlayHistory() {
  fetch("activity_history.json")
    .then((response) => response.json())
    .then((data) => {
      if (data.length == 0) {
        processedIds = new Set();
      }
      const recentActivityDiv = document.querySelector(".recent-activity");
      
      // Process entries in reverse order to show newest first
      data.forEach((entry) => {
        if (!processedIds.has(entry.id)) {
          let activityDiv;
          if (entry.type == "score") {
            activityDiv = createPlayEntry(entry);
          } else {
            activityDiv = createMedalEntry(entry);
          }
          
          // Add new entry at the top with animation
          recentActivityDiv.prepend(activityDiv);
          requestAnimationFrame(() => {
            activityDiv.style.maxHeight = '0';
            activityDiv.style.opacity = '0';
            activityDiv.style.transition = 'max-height 0.5s ease-out, opacity 0.5s ease-out';
            
            requestAnimationFrame(() => {
              activityDiv.style.maxHeight = '500px'; // Adjust based on your max entry height
              activityDiv.style.opacity = '1';
            });
          });

          // Add to processed IDs
          processedIds.add(entry.id);
        }
      });
    })
    .catch((error) => console.error("Error fetching play history:", error));
}

// Function to create a play entry
function createPlayEntry(entry) {
  const playDiv = document.createElement("div");
  playDiv.className = "recent-play";

  // Grade
  const gradeMap = { 0: "XH", 1: "SH", 2: "X", 3: "S", 4: "A", 5: "B", 6: "C", 7: "D", 9: "F" };
  const gradeDiv = document.createElement("div");
  gradeDiv.className = `grade grade--${gradeMap[entry.grade]}`;
  playDiv.appendChild(gradeDiv);

  // Score info
  const scoreInfoDiv = document.createElement("div");
  scoreInfoDiv.className = "score-info";

  // Set info
  const setInfoDiv = document.createElement("div");
  setInfoDiv.className = "set-info";
  const songNameDiv = document.createElement("div");
  songNameDiv.className = "song-name";
  songNameDiv.innerHTML = `${entry.titleRoman} <span class="artist">by ${entry.artistRoman}</span>`;
  setInfoDiv.appendChild(songNameDiv);
  scoreInfoDiv.appendChild(setInfoDiv);

  // Statistics
  const statisticsDiv = document.createElement("div");
  statisticsDiv.className = "statistics";
  statisticsDiv.textContent = `${entry.score.toLocaleString()} / ${
    entry.currentMaxCombo
  }x { ${entry.c300} / ${entry.geki} // ${entry.c100} / ${entry.katsu} // ${
    entry.c50
  } / ${entry.miss} }`;
  scoreInfoDiv.appendChild(statisticsDiv);

  // Score footer
  const scoreFooterDiv = document.createElement("div");
  scoreFooterDiv.className = "score-footer";

  // Game mode
  const gameModeDiv = document.createElement("div");
  gameModeDiv.className = `gamemode gamemode--${entry.gameMode}`;
  scoreFooterDiv.appendChild(gameModeDiv);

  // Difficulty name
  const diffNameDiv = document.createElement("div");
  diffNameDiv.className = "diff-name";
  diffNameDiv.textContent = entry.diffName;
  scoreFooterDiv.appendChild(diffNameDiv);

  // Timestamp
  const timestampDiv = document.createElement("div");
  timestampDiv.className = "timestamp";
  const elapsedTime = entry.elapsed_time;
  const currentTime = entry.current_time;

  // Convert elapsed time to hh:mm:ss.xxx format
  const milliseconds = Math.floor((elapsedTime * 1000) % 1000);
  const seconds = Math.floor(elapsedTime % 60);
  const minutes = Math.floor((elapsedTime / 60) % 60);
  const hours = Math.floor((elapsedTime / (60 * 60)) % 24);
  const formattedElapsedTime = 
    `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds).padStart(3, '0')}`;

  // Format date and time
  const currentTimeDate = new Date(currentTime);
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' };
  const formattedDate = currentTimeDate.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
  const formattedTime = currentTimeDate.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const timezone = currentTimeDate.toTimeString().match(/\(([^)]+)\)/)[1]; // Extract the timezone

  timestampDiv.innerHTML = `${formattedElapsedTime} <div class="tooltip"><span class="tooltip-date">${formattedDate}</span> <span class="tooltip-time">${formattedTime} ${timezone}</span></div>`;
  scoreFooterDiv.appendChild(timestampDiv);

  scoreInfoDiv.appendChild(scoreFooterDiv);
  playDiv.appendChild(scoreInfoDiv);

  // Mods
  const modsDiv = document.createElement("div");
  modsDiv.className = "mods";
  const mods = [
    { flag: 1, name: "NF", tooltip: "No Fail" },
    { flag: 2, name: "EZ", tooltip: "Easy" },
    { flag: 4, name: "TD", tooltip: "Touch Device" },
    { flag: 8, name: "HD", tooltip: "Hidden" },
    { flag: 16, name: "HR", tooltip: "Hard Rock" },
    { flag: 32, name: "SD", tooltip: "Sudden Death" },
    { flag: 64, name: "DT", tooltip: "Double Time" },
    { flag: 128, name: "RX", tooltip: "Relax" },
    { flag: 256, name: "HT", tooltip: "Half Time" },
    { flag: 512, name: "NC", tooltip: "Nightcore" },
    { flag: 1024, name: "FL", tooltip: "Flashlight" },
    { flag: 2048, name: "AT", tooltip: "Autoplay" },
    { flag: 4096, name: "SO", tooltip: "Spun Out" },
    { flag: 8192, name: "AP", tooltip: "Autopilot" },
    { flag: 16384, name: "PF", tooltip: "Perfect" },
    { flag: 32768, name: "4K", tooltip: "4K" },
    { flag: 65536, name: "5K", tooltip: "5K" },
    { flag: 131072, name: "6K", tooltip: "6K" },
    { flag: 262144, name: "7K", tooltip: "7K" },
    { flag: 524288, name: "8K", tooltip: "8K" },
    { flag: 1048576, name: "FI", tooltip: "Fade In" },
    { flag: 2097152, name: "RD", tooltip: "Random" },
    { flag: 4194304, name: "CN", tooltip: "Cinema" },
    { flag: 8388608, name: "TP", tooltip: "Target Practice" },
    { flag: 16777216, name: "9K", tooltip: "9K" },
    { flag: 33554432, name: "CO", tooltip: "Co-op" },
    { flag: 67108864, name: "1K", tooltip: "1K" },
    { flag: 134217728, name: "3K", tooltip: "3K" },
    { flag: 268435456, name: "2K", tooltip: "2K" },
    { flag: 536870912, name: "V2", tooltip: "ScoreV2" },
    { flag: 1073741824, name: "MR", tooltip: "Mirror" }
  ];

  mods.forEach((mod) => {
    if (entry.modsEnum & mod.flag) {
      if (mod.name == "DT" && entry.modsEnum & 512) return;
      if (mod.name == "SD" && entry.modsEnum & 16384) return;
      const modDiv = document.createElement("div");
      modDiv.className = `mod mod--${mod.name}`;
      modDiv.innerHTML = `<div class="tooltip">${mod.tooltip}</div>`;
      modsDiv.appendChild(modDiv);
    }
  });

  playDiv.appendChild(modsDiv);

  // Accuracy
  const accuracyDiv = document.createElement("div");
  const accuracyVal = entry.acc * 100;
  accuracyDiv.className = "accuracy";
  accuracyDiv.textContent = `${accuracyVal.toFixed(2)}%`;
  playDiv.appendChild(accuracyDiv);

  return playDiv;
}

// Function to create a medal entry
function createMedalEntry(entry) {
  const medalDiv = document.createElement("div");
  medalDiv.className = "medal-unlock";

  // Medal count
  const medalCountDiv = document.createElement("div");
  medalCountDiv.className = "medal-count";
  medalCountDiv.textContent = entry.count;
  medalDiv.appendChild(medalCountDiv);

  // Medal unlock content
  const medalUnlockContentDiv = document.createElement("div");
  medalUnlockContentDiv.className = "medal-unlock-content";

  // Medal background image
  const medalBackgroundImg = document.createElement("img");
  medalBackgroundImg.className = "medal-background";
  medalBackgroundImg.src = `assets/images/medals/${entry.medal_id}.png`;
  medalUnlockContentDiv.appendChild(medalBackgroundImg);

  // Medal icon
  const medalIconDiv = document.createElement("div");
  medalIconDiv.className = "medal-icon";
  const medalIconImg = document.createElement("img");
  medalIconImg.src = `assets/images/medals/${entry.medal_id}.png`;
  medalIconDiv.appendChild(medalIconImg);
  medalUnlockContentDiv.appendChild(medalIconDiv);

  // Medal info
  const medalInfoDiv = document.createElement("div");
  medalInfoDiv.className = "medal-info";

  const medalNameDiv = document.createElement("div");
  medalNameDiv.className = "medal-name";
  medalNameDiv.textContent = entry.name;
  medalInfoDiv.appendChild(medalNameDiv);

  const medalDescriptionDiv = document.createElement("div");
  medalDescriptionDiv.className = "medal-description";
  medalDescriptionDiv.textContent = entry.description;
  medalInfoDiv.appendChild(medalDescriptionDiv);

  medalUnlockContentDiv.appendChild(medalInfoDiv);

  // Medal timestamp
  const medalTimestampDiv = document.createElement("div");
  medalTimestampDiv.className = "medal-timestamp";

  // Convert elapsed time to hh:mm:ss.xxx format
  const elapsedTime = entry.elapsed_time;
  const milliseconds = Math.floor((elapsedTime * 1000) % 1000);
  const seconds = Math.floor(elapsedTime % 60);
  const minutes = Math.floor((elapsedTime / 60) % 60);
  const hours = Math.floor((elapsedTime / (60 * 60)) % 24);

  const formattedElapsedTime = 
    `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds).padStart(3, '0')}`;

  medalTimestampDiv.textContent = formattedElapsedTime;
  medalUnlockContentDiv.appendChild(medalTimestampDiv);

  medalDiv.appendChild(medalUnlockContentDiv);

  return medalDiv;
}

// Fetch and poll for changes
fetchAndProcessPlayHistory();
setInterval(fetchAndProcessPlayHistory, 5000);
