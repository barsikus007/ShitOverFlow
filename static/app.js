// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                  event.preventDefault()
                  event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})()

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

function commentSendPreview(index) {
    let addButton = document.querySelector(`#answer-${index} div.comment-button`);
    addButton.innerHTML =
        `<form name="createComment">
            <div class="row">
                <div class="col-sm-6">
                    <input type="text" name="comment" class="form-control" placeholder="Comment" aria-label="Comment">
                </div>
                <div class="col-sm">
                    <input type="text" name="name" class="form-control" placeholder="Name" aria-label="Name">
                </div>
                <div class="col-sm">
                    <button type="button" class="btn btn-primary button-send" onclick="commentPush(${index})">Add comment</button>
                </div>  
            </div>
         </form>`;
}

function commentPush(index) {
    let commentForm = document.forms.createComment;
    let commentText = commentForm.elements.comment.value;
    let commentAuthor = commentForm.elements.name.value;

    fetch(`http://shitoverflow.tmweb.ru/api/v1/answer/${index}/comments/add`,
        { method: 'POST', body: `{"author": "${commentAuthor}", "body": "${commentText}"}` })
        .then(result => result.json())
        .then(() => window.location.reload());

    return false;
}