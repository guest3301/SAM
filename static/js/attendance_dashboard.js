document.getElementById('fetch-low-attendance').addEventListener('click', function() {
    const classID = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    const year = document.getElementById('year-select').value;
    const month = document.getElementById('month-select').value;

    if (classID && subject && year && month) {
        fetch(`/attendance/low-attendance?class_id=${classID}&subject=${subject}&year=${year}&month=${month}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector('#low-attendance-table tbody');
                tableBody.innerHTML = '';  // Clear previous results

                data.students.forEach(student => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${student.roll_no}</td>
                        <td>${student.name}</td>
                        <td>${student.attendance_percentage.toFixed(2)}%</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error fetching low attendance data:', error);
            });
    } else {
        alert('Please select class, subject, year, and month.');
    }
});

document.getElementById('populate-dummy-data').addEventListener('click', function() {
    const classID = document.getElementById('dummy-class-select').value;
    const subject = document.getElementById('dummy-subject-select').value;
    const days = document.getElementById('days-input').value;

    if (classID && subject && days) {
        const formData = new FormData();
        formData.append('class_id', classID);
        formData.append('subject', subject);
        formData.append('days', days);

        fetch('/attendance/populate-dummy', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Dummy data populated successfully.');
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error populating dummy data:', error);
        });
    } else {
        alert('Please fill out all fields.');
    }
});
function date() {
    var today = new Date();
    var day = String(today.getDate()).padStart(2, '0');
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var year = today.getFullYear();
    var formattedDate = year + '-' + month + '-' + day;
    return [year, month, day];
}
var date = date();
document.getElementById('year-select').value = date[0];
document.getElementById('month-select').value = date[1];
