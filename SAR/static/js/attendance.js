document.getElementById('view-attendance').addEventListener('click', function() {
    const date = document.getElementById('attendance-date').value;
    const classID = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    if (date && classID) {
        fetch(`/attendance?date=${date}&class_id=${classID}&subject=${subject}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('students-container');
                container.innerHTML = '';
                data.forEach(student => {
                    const studentDiv = document.createElement('div');
                    studentDiv.id = `student-${student.id}`;
                    studentDiv.className = student.present ? 'student-div present' : 'student-div absent';
                    studentDiv.innerText = `${student.roll_no} - ${student.name}`;
                    container.appendChild(studentDiv);
                });
            });
    } else {
        alert('Please select a date, subject and class.');
    }
});

document.getElementById('x').addEventListener('change', function() {
    const classID = document.getElementById('class-select').value;
    if (classID) {
        fetch(`/api/attendance/students?class_id=${classID}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('students-container');
                container.innerHTML = '';
                data.forEach(student => {
                    const studentDiv = document.createElement('div');
                    studentDiv.id = `student-${student.id}`;
                    studentDiv.className = 'student-div absent';
                    studentDiv.innerText = `${student.roll_no} - ${student.name}`;
                    studentDiv.addEventListener('click', function() {
                        this.classList.toggle('present');
                        this.classList.toggle('absent');
                    });
                    container.appendChild(studentDiv);
                });
            });
    }
});

document.getElementById('submit-attendance').addEventListener('click', function() {
    const class_id = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    let attendance = [];
    document.querySelectorAll('.student-div.present').forEach((div) => {
        attendance.push({
            student_id: parseInt(div.id.split('-')[1]),
            present: true,
        });
    });
    document.querySelectorAll('.student-div.absent').forEach((div) => {
        attendance.push({
            student_id: parseInt(div.id.split('-')[1]),
            present: false,
        });
    });
    fetch('/api/attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'attendance': attendance, 'class_id': class_id, 'subject': subject }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('students-container').innerHTML = '';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

window.onload = function() {
    var today = new Date();
    var day = String(today.getDate()).padStart(2, '0');
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var year = today.getFullYear();
    var formattedDate = year + '-' + month + '-' + day;
    document.getElementById('attendance-date').value = formattedDate;
};
