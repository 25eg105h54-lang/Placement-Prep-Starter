const API_URL = 'http://127.0.0.1:5000';
let currentWeek = 1;
let authToken = null;
let currentUser = null;

const roadmap = {
1:{resources:[{name:"C Tutorial",link:"https://www.youtube.com"},
              {name:"Practice Problems",link:"https://www.hackerrank.com"}]},
2:{resources:[{name:"Arrays Guide",link:"https://www.geeksforgeeks.org"}]},
3:{resources:[{name:"Pointers Video",link:"https://www.youtube.com"}]},
4:{resources:[{name:"Git Guide",link:"https://git-scm.com"}]},
5:{resources:[{name:"LinkedIn",link:"https://www.linkedin.com"}]},
6:{resources:[{name:"Interview Prep",link:"https://www.indeed.com"}]},
7:{resources:[{name:"LeetCode",link:"https://leetcode.com"}]},
8:{resources:[{name:"Resume Guide",link:"https://novoresume.com"}]}
};

// ==================== AUTH FUNCTIONS ====================

function toggleAuthForm(e) {
    e.preventDefault();
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const authTitle = document.getElementById('authTitle');
    
    if(loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        authTitle.textContent = 'Login';
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        authTitle.textContent = 'Sign Up';
    }
}

function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    
    if(!email || !password) {
        alert('Please enter email and password');
        return;
    }
    
    fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    })
    .then(r => r.json())
    .then(data => {
        if(data.error) {
            alert('Login failed: ' + data.error);
            return;
        }
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        document.getElementById('authModal').style.display = 'none';
        updateUI();
        loadWeek(1, document.querySelector('.week-btn'));
    })
    .catch(err => alert('Login error: ' + err));
}

function handleSignup() {
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value.trim();
    
    if(!name || !email || !password) {
        alert('Please fill all fields');
        return;
    }
    
    fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password})
    })
    .then(r => r.json())
    .then(data => {
        if(data.error) {
            alert('Signup failed: ' + data.error);
            return;
        }
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        document.getElementById('authModal').style.display = 'none';
        updateUI();
        loadWeek(1, document.querySelector('.week-btn'));
    })
    .catch(err => alert('Signup error: ' + err));
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    document.getElementById('authModal').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
}

function updateUI() {
    if(currentUser) {
        document.getElementById('welcomeMsg').textContent = `Welcome, ${currentUser.name}! 👋`;
    }
}

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    };
}

// ==================== TASK FUNCTIONS ====================

function loadWeek(week, btn) {
    if(!authToken) return;
    
    currentWeek = week;
    document.querySelectorAll('.week-btn').forEach(b => b.classList.remove('active'));
    if(btn) btn.classList.add('active');
    
    const tasksDiv = document.getElementById('tasks');
    const resDiv = document.getElementById('resources');
    tasksDiv.innerHTML = '';
    resDiv.innerHTML = '';
    
    // Show resources
    if(roadmap[week]) {
        roadmap[week].resources.forEach(r => {
            const link = document.createElement('a');
            link.href = r.link;
            link.target = '_blank';
            link.innerText = r.name;
            resDiv.appendChild(link);
            resDiv.appendChild(document.createElement('br'));
        });
    }
    
    // Fetch tasks from backend
    fetch(`${API_URL}/api/tasks/week/${week}`, {
        headers: getHeaders()
    })
    .then(r => r.json())
    .then(tasks => {
        tasks.forEach(t => {
            const div = document.createElement('div');
            div.className = 'task-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = t.completed;
            
            checkbox.onchange = function() {
                updateTaskStatus(t.id, !t.completed, week);
            };
            
            div.appendChild(checkbox);
            div.append(t.title);
            tasksDiv.appendChild(div);
        });
        updateProgress(week);
    })
    .catch(err => console.error('Error fetching tasks:', err));
}

function updateTaskStatus(taskId, completed, week) {
    fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({completed})
    })
    .then(r => r.json())
    .then(data => {
        updateProgress(week);
    })
    .catch(err => console.error('Error updating task:', err));
}

function addTask() {
    if(!authToken) return;
    
    const title = document.getElementById('newTitle').value.trim();
    const week = parseInt(document.getElementById('newWeek').value, 10);
    
    if(!title || !week || week < 1 || week > 8) {
        alert('Please enter valid task and week');
        return;
    }
    
    fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({title, week})
    })
    .then(r => r.json())
    .then(task => {
        document.getElementById('newTitle').value = '';
        document.getElementById('newWeek').value = '';
        if(week === currentWeek) {
            loadWeek(currentWeek, document.querySelector('.week-btn.active'));
        } else {
            alert('Task added to week ' + week);
        }
    })
    .catch(err => console.error('Error adding task:', err));
}

function updateProgress(week) {
    if(!authToken) return;
    
    // Weekly progress from DOM
    const checkboxes = document.querySelectorAll('#tasks input');
    let checked = 0;
    checkboxes.forEach(box => {if(box.checked) checked++;});
    let percent = checkboxes.length ? (checked / checkboxes.length) * 100 : 0;
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('percentText').innerText = Math.round(percent) + '% Completed';
    if(percent === 100) showCertificate();
    
    // Overall progress from backend
    fetch(`${API_URL}/api/progress/overall`, {
        headers: getHeaders()
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById('overallBar').style.width = data.progress + '%';
        document.getElementById('overallText').innerText = Math.round(data.progress) + '% Completed';
    })
    .catch(err => console.error('Error fetching progress:', err));
}

function showCertificate() {
    const name = currentUser ? currentUser.name : 'Student';
    document.getElementById('certificateText').innerText = 
        name + ' has successfully completed this week\'s roadmap!';
    document.getElementById('certificateModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('certificateModal').style.display = 'none';
}

// ==================== INITIALIZATION ====================

window.onload = function() {
    // Check if already logged in
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if(savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        document.getElementById('authModal').style.display = 'none';
        updateUI();
        loadWeek(1, document.querySelector('.week-btn'));
    } else {
        document.getElementById('authModal').style.display = 'flex';
    }
};