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

window.onload = () => {
    let commentsBlockArray = document.getElementsByClassName('comment-block');

    for (let comment in commentsBlockArray) {

        if (comments.length === 5) {
            commentBlock.getElementsByClassName('comment-button');
            commentBlock.innerHTML(`<div class='col-3'>
            <div class="load-button">

            </div></div>`)
        }
    });
}

function changeCommentPage() {
    let prevButton = document.getElementsByClassName("button-prev");
    let nextButton = document.getElementsByClassName("button-next");
    let pageNum = document.getElementsByClassName("page-number");
    let questions = fetch(`/api/v1/questions?page=${2}`)
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

function vote(post_type, post_id, action, undo = false) {
    let undo_str = undo ? '/undo' : ''
    fetch(`/api/v1/${post_type}/${post_id}/${action}${undo_str}`,
        {method: 'POST'})
        .then(result => result.json())
        .then((data) => {
            if (data.success) {
                let upvoteButton = document.querySelector(`#${post_type}-${post_id} div.vote button.arrow-up`);
                let score_cnt = document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML;
                let downvoteButton = document.querySelector(`#${post_type}-${post_id} div.vote button.arrow-down`);
                if (!undo) {
                    if (action === 'upvote') {
                        upvoteButton.classList.add('upvote')
                        let onclick = upvoteButton.getAttribute('onclick')
                        upvoteButton.setAttribute('onclick', onclick.slice(0, -1)+', true)');
                        downvoteButton.classList.add('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = +score_cnt + 1;
                    } else {
                        downvoteButton.classList.add('downvote')
                        let onclick = downvoteButton.getAttribute('onclick')
                        downvoteButton.setAttribute('onclick', onclick.slice(0, -1)+', true)');
                        upvoteButton.classList.add('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = +score_cnt - 1;
                    }
                } else {
                    if (action === 'upvote') {
                        upvoteButton.classList.remove('upvote')
                        let onclick = upvoteButton.getAttribute('onclick')
                        upvoteButton.setAttribute('onclick', onclick.slice(0, -7)+')');
                        downvoteButton.classList.remove('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = +score_cnt - 1;
                    } else {
                        downvoteButton.classList.remove('downvote')
                        let onclick = downvoteButton.getAttribute('onclick')
                        downvoteButton.setAttribute('onclick', onclick.slice(0, -7)+')');
                        upvoteButton.classList.remove('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = +score_cnt - 1;
                    }
                }
            }
        });

    return false;
}

function commentSendPreview(post_type, post_id) {
    let addButton = document.querySelector(`#${post_type}-${post_id} div.comment-button`);
    addButton.innerHTML =
        `<form name="create-comment" >
    <div class="row form-floating">
        <div class="col-sm-6">
            <input type="text" name="comment" class="form-control" placeholder="Comment" required>
            <div class="invalid-feedback">Please choose your name (3-64 symbols)</div>
        </div>
        <div class="col-sm">
            <input type="text" name="name" class="form-control" placeholder="Name" required>
            <div class="invalid-feedback">Please specify comment</div>
        </div>
        <div class="col-sm">
            <button type="button" class="btn btn-primary button-send" onclick="commentPush('${post_type}', ${post_id})">Add comment</button>
        </div>  
    </div>
 </form>`;
}

function commentPush(post_type, post_id) {
    let commentForm = document.forms['create-comment'];
    let commentText = commentForm.elements.comment.value;
    let commentAuthor = commentForm.elements.name.value;
    if (!commentForm.checkValidity()) {
        this.event.preventDefault();
        this.event.stopPropagation();
        return false
    }
    commentForm.classList.add('was-validated');
    fetch(`/api/v1/${post_type}/${post_id}/comments/add`,
        {method: 'POST', body: `{"author": "${commentAuthor}", "body": "${commentText}"}`})
        .then(result => result.json())
        .then(() => window.location.reload());
    return false
}

function join(t) {
    let dateArray = [{day: 'numeric'}, {month: 'short'}, {year: 'numeric'}];

   function format(m) {
      let f = new Intl.DateTimeFormat('en', m);
      return f.format(t);
   }
   return dateArray.map(format).join('-');
}

