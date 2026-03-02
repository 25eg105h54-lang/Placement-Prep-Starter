const roadmap = {
1:{tasks:["C Basics","Variables & Loops","10 Problems"],
   resources:[{name:"C Tutorial",link:"https://www.youtube.com"},
              {name:"Practice Problems",link:"https://www.hackerrank.com"}]},
2:{tasks:["Functions","Arrays","20 Problems"],
   resources:[{name:"Arrays Guide",link:"https://www.geeksforgeeks.org"}]},
3:{tasks:["Pointers","Strings","Mini Project"],
   resources:[{name:"Pointers Video",link:"https://www.youtube.com"}]},
4:{tasks:["Git Basics","GitHub Setup","Push Repo"],
   resources:[{name:"Git Guide",link:"https://git-scm.com"}]},
5:{tasks:["LinkedIn Profile","Add Skills","Connect Seniors"],
   resources:[{name:"LinkedIn",link:"https://www.linkedin.com"}]},
6:{tasks:["Communication Practice","Self Intro","Interview Qs"],
   resources:[{name:"Interview Prep",link:"https://www.indeed.com"}]},
7:{tasks:["Start DSA","3 Problems Daily"],
   resources:[{name:"LeetCode",link:"https://leetcode.com"}]},
8:{tasks:["Mock Interview","Revise","Resume Build"],
   resources:[{name:"Resume Guide",link:"https://novoresume.com"}]}
};

function loadWeek(week,btn){
document.querySelectorAll(".week-btn").forEach(b=>b.classList.remove("active"));
if(btn) btn.classList.add("active");

const tasksDiv=document.getElementById("tasks");
const resDiv=document.getElementById("resources");
tasksDiv.innerHTML="";
resDiv.innerHTML="";

roadmap[week].tasks.forEach((task,index)=>{
    const div=document.createElement("div");
    div.className="task-item";

    const checkbox=document.createElement("input");
    checkbox.type="checkbox";
    checkbox.id=week+"_"+index;
    checkbox.checked=localStorage.getItem(checkbox.id)==="true";

    checkbox.onchange=function(){
        localStorage.setItem(checkbox.id,checkbox.checked);
        updateProgress(week);
        updateOverall();
    };

    div.appendChild(checkbox);
    div.append(task);
    tasksDiv.appendChild(div);
});

roadmap[week].resources.forEach(r=>{
    const link=document.createElement("a");
    link.href=r.link;
    link.target="_blank";
    link.innerText=r.name;
    resDiv.appendChild(link);
    resDiv.appendChild(document.createElement("br"));
});

updateProgress(week);
updateOverall();
}

function updateProgress(week){
const checkboxes=document.querySelectorAll("#tasks input");
let checked=0;
checkboxes.forEach(box=>{if(box.checked)checked++;});
let percent=(checked/checkboxes.length)*100;
document.getElementById("progressBar").style.width=percent+"%";
document.getElementById("percentText").innerText=Math.round(percent)+"% Completed";
if(percent===100) showCertificate();
}

function updateOverall(){
let total=0,completed=0;
for(let w=1;w<=8;w++){
roadmap[w].tasks.forEach((t,i)=>{
total++;
if(localStorage.getItem(w+"_"+i)==="true") completed++;
});
}
let percent=(completed/total)*100;
document.getElementById("overallBar").style.width=percent+"%";
document.getElementById("overallText").innerText=Math.round(percent)+"% Completed";
}

function saveName(){
const name=document.getElementById("username").value;
localStorage.setItem("username",name);
document.getElementById("welcomeMsg").innerText="Welcome, "+name+" 👋";
}

function showCertificate(){
const name=localStorage.getItem("username")||"Student";
document.getElementById("certificateText").innerText=
name+" has successfully completed this week's roadmap!";
document.getElementById("certificateModal").style.display="flex";
}

function closeModal(){
document.getElementById("certificateModal").style.display="none";
}

window.onload=function(){
const savedName=localStorage.getItem("username");
if(savedName){
document.getElementById("welcomeMsg").innerText="Welcome, "+savedName+" 👋";
}
loadWeek(1,document.querySelector(".week-btn"));
}