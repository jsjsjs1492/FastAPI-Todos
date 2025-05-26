// ... 기존 코드 ...

document.addEventListener('DOMContentLoaded', function() {
    // ... 기존 코드 ...
    
    // 달력 기능 구현
    const calendarContainer = document.getElementById('calendar-container');
    if (calendarContainer) {
        const monthYearDisplay = document.getElementById('month-year');
        const calendarDays = document.getElementById('calendar-days');
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');

        // 요소가 존재하는지 확인하고 콘솔에 로그 출력
        console.log('Calendar elements:', {
            container: calendarContainer,
            monthYear: monthYearDisplay,
            days: calendarDays,
            prevBtn: prevMonthBtn,
            nextBtn: nextMonthBtn
        });

        const today = new Date();
        let currentMonth = today.getMonth();
        let currentYear = today.getFullYear();
        let selectedDate = today;

        const monthNames = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"];

        function renderCalendar(month, year) {
            if (!monthYearDisplay || !calendarDays) {
                console.error('Calendar elements not found');
                return;
            }

            // 디버깅을 위한 로그
            console.log(`Rendering calendar for ${year}년 ${monthNames[month]}`);
            
            calendarDays.innerHTML = '';
            monthYearDisplay.textContent = `${year}년 ${monthNames[month]}`;

            const firstDayOfMonth = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            
            console.log(`First day: ${firstDayOfMonth}, Days in month: ${daysInMonth}`);

            let date = 1;
            for (let i = 0; i < 6; i++) {
                const row = document.createElement('tr');

                for (let j = 0; j < 7; j++) {
                    const cell = document.createElement('td');
                    
                    // 주말 클래스 추가
                    if (j === 0 || j === 6) {
                        cell.classList.add('weekend');
                    }
                    
                    if (i === 0 && j < firstDayOfMonth) {
                        // 달의 첫 날짜 이전의 빈 칸
                        cell.textContent = '';
                    } else if (date > daysInMonth) {
                        // 달의 마지막 날짜 이후의 빈 칸
                        cell.textContent = '';
                    } else {
                        cell.textContent = date;
                        
                        // 날짜 클릭 이벤트 추가
                        cell.addEventListener('click', function() {
                            const clickedDate = new Date(year, month, parseInt(this.textContent));
                            selectDate(clickedDate);
                        });
                        
                        // 오늘 날짜인지 확인
                        if (date === today.getDate() && year === today.getFullYear() && month === today.getMonth()) {
                            cell.classList.add('today');
                        }
                        
                        // 선택된 날짜인지 확인
                        const cellDate = new Date(year, month, date);
                        if (selectedDate && 
                            cellDate.getDate() === selectedDate.getDate() && 
                            cellDate.getMonth() === selectedDate.getMonth() && 
                            cellDate.getFullYear() === selectedDate.getFullYear()) {
                            cell.classList.add('selected');
                        }
                        
                        date++;
                    }
                    row.appendChild(cell);
                }
                calendarDays.appendChild(row);

                // 모든 날짜가 표시되었으면 루프 중단
                if (date > daysInMonth) {
                    break;
                }
            }
        }

        function selectDate(date) {
            selectedDate = date;
            renderCalendar(currentMonth, currentYear);
            
            // 여기에 선택한 날짜에 대한 추가 작업을 수행할 수 있습니다
            console.log(`선택된 날짜: ${date.toLocaleDateString('ko-KR')}`);
            
            // 선택한 날짜에 해당하는 할 일 필터링 기능을 여기에 추가할 수 있습니다
            // filterTodosByDate(date);
        }

        // 이전 달 버튼 클릭 이벤트
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', function() {
                currentMonth--;
                if (currentMonth < 0) {
                    currentMonth = 11;
                    currentYear--;
                }
                renderCalendar(currentMonth, currentYear);
            });
        }

        // 다음 달 버튼 클릭 이벤트
        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', function() {
                currentMonth++;
                if (currentMonth > 11) {
                    currentMonth = 0;
                    currentYear++;
                }
                renderCalendar(currentMonth, currentYear);
            });
        }

        // 초기 달력 렌더링
        renderCalendar(currentMonth, currentYear);
    } else {
        console.error('Calendar container not found');
    }
    
    // ... 기존 코드 ...
});

// ... 기존 코드 ...