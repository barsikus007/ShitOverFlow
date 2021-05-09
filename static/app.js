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

function addComments(post_type, post_id) {
    let comments = fetch(`/api/v1/${post_type}/${post_id}/comments`)
        .then(result => result.json())
        .then(data => {
            console.log(data);
            let commentss = data.comments.slice(5);
            let comments_block = document.querySelector(`#${post_type}-${post_id} .comments-block`)
            commentss.forEach((comment) => {
                let score = 0;
                if (comment.score_data != null) {
                    score = comment.score_data * 1 + (!comment.score_data) * -1;
                }
                let raw_html = `<div class="comment row d-flex justify-content-center comment-vote pb-3"
                                     id="comment-{{ comment.id }}">
                                    <div class="col-1">
                                        <div class="comment-vote">
                                            <div class="row">
                                                <button class="${(score === 1) ? 'upvote ' : (score === -1) ? 'unclickable ' : ''}arrow-up" onclick="vote('comment', ${comment.id}, 'upvote', ${score === 1})">
                                                    <svg class="svg-icon iconArrowUpLg"
                                                         aria-hidden="true" width="18" height="18" viewBox="0 0 36 36">
                                                        <path d="M2 26h32L18 10 2 26z"></path>
                                                    </svg>
                                                </button>
                                            </div>

                                            <div class="row d-flex justify-content-center vote-count comment-vote">${comment.score}</div>

                                            <div class="row">
                                                <button class="${(score === -1) ? 'downvote ' : (score === 1) ? 'unclickable ' : ''}arrow-down" onclick="vote('comment', ${comment.id}, 'downvote', ${score === -1})">
                                                    <svg class="m0 svg-icon iconArrowDownLg"
                                                         aria-hidden="true" width="18" height="18" viewBox="0 0 36 36">
                                                        <path d="M2 10h32L18 26 2 10z"></path>
                                                    </svg>
                                                </button>
                                            </div>

                                        </div>
                                    </div>

                                    <div class="col-11 comment-text text-break">
                                        <span>${comment.body}</span>
                                        <span class="fine-text"
                                              title="{{ comment.created_at.strftime('%H:%M:%S %d.%m.%Y') }}">– ${comment.author}</span>
                                    </div>
                                </div>
                                    <hr>`
                comments_block.insertAdjacentHTML('beforeend', raw_html);
            })
            document.querySelector(`#${post_type}-${post_id} .comment-button-load`).remove()
        });


    console.log(comments);
}

window.onload = () => {
    let commentsBlockArray = document.getElementsByClassName('comments-block')
    console.log(commentsBlockArray[0])

    Array.prototype.forEach.call(commentsBlockArray, (commentBlock) => {
        let comments = commentBlock.getElementsByClassName('comment');

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

