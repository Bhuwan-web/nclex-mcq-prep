function updateInputsFromState() {
    const state = getUserState();
    document.getElementById('page_size').value = state.pageSize;
    document.getElementById('start_from').value = state.startFrom;
}

async function loadQuestions() {
    const pageSize = document.getElementById('page_size').value;
    const startFrom = document.getElementById('start_from').value;
    saveUserState(startFrom, pageSize);
    const res = await fetch(`/questions/?page_size=${pageSize}&start_from=${startFrom}`);
    const questions = await res.json();
    const container = document.getElementById('question-list');
    container.innerHTML = '';
    questions.forEach(qwrap => {
        const q = qwrap.question;
        const block = document.createElement('div');
        block.className = 'question-block';
        block.innerHTML = `<b>Q${q.question_number}:</b> ${q.question_text}<br>` +
            ['A','B','C','D'].map(opt =>
                `<button class='option-btn' data-qid='${q.id}' data-opt='${opt}'>${opt}: ${q['option_' + opt.toLowerCase()]}</button>`
            ).join('');
        container.appendChild(block);
    });
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.onclick = async function() {
            const qid = this.dataset.qid;
            const res = await fetch(`/question/${qid}/answer`);
            if (res.ok) {
                const data = await res.json();
                document.getElementById('answer-container').style.display = 'block';
                document.getElementById('correct-answer').textContent = data.answer;
                document.getElementById('rationale').textContent = data.rationale;
            } else {
                document.getElementById('answer-container').style.display = 'block';
                document.getElementById('correct-answer').textContent = 'Not found';
                document.getElementById('rationale').textContent = '';
            }
        };
    });
}

window.onload = function() {
    updateInputsFromState();
    loadQuestions();
};
