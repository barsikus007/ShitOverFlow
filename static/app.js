function createThread(){
    let form = document.forms.create;
    let author = form.elements.author.value;
    let title = form.elements.title.value;
    let body = form.elements.body.value;
    let tags = form.elements.tags.value;


}

function changeCommentPage() {
    let prevButton = document.getElementsByClassName("button-prev");
    let nextButton = document.getElementsByClassName("button-next");
    let pageNum = document.getElementsByClassName("page-number");
    let questions = fetch(`http://shitoverflow.tmweb.ru/api/v1/questions?page=${2}`)
        .then(response => response.json())
        .then(data => data.questions.forEach(function (question, ind) {
                ques_link[ind].href = `/questions/${question.id}`;
                ques_link[ind].innerText = question.title;
            }));
    console.log(ind)
    let questionsCount = 10;
    //let maxPages = Math.ceil(questionsCount / 10);

    if (pageNum < 1) {
        pageNum = 1;
    }
}

function like() {
    let prevButton = document.getElementsByClassName("button-prev");
    let nextButton = document.getElementsByClassName("button-next");
    let pageNum = document.getElementsByClassName("page-number");
    let questions = fetch(`http://shitoverflow.tmweb.ru/api/v1/questions?page=${2}`)
        .then(response => response.json())
        .then(data => data.questions.forEach(function (question, ind) {
                ques_link[ind].href = `/questions/${question.id}`;
                ques_link[ind].innerText = question.title;
            }));
    console.log(ind)
    let questionsCount = 10;
    //let maxPages = Math.ceil(questionsCount / 10);

    if (pageNum < 1) {
        pageNum = 1;
    }
}