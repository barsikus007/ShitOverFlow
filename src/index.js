'use strict';
// function checker(form) {
//     let comment = form.elements.comment.value;
//     let name = form.elements.name.value;
//     if (name.length >= 2 && name.length <= 64 && comment.length >= 3 ) {
//         return true
//     }
// }

ReactDOM.render(
    <React.StrictMode>
        <CreateThread />
    </React.StrictMode>,
    document.getElementById('form_block')
);

Date.prototype.format = function (format) {
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const shortMonthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ];

    let yyyy = this.getFullYear();
    let yy = yyyy.toString().substring(2);
    let m = this.getMonth() + 1;
    let mm = m < 10 ? '0' + m : m;
    let d = this.getDate();
    let dd = d < 10 ? '0' + d : d;

    let H = this.getHours();
    let HH = H < 10 ? '0' + H : H;
    let M = this.getMinutes();
    let MM = M < 10 ? '0' + M : M;
    let S = this.getSeconds();
    let SS = S < 10 ? '0' + S : S;

    format = format.replace(/%Y/i, yy);
    format = format.replace(/%M/i, mm);
    format = format.replace(/%d/i, dd);
    format = format.replace(/%HH/i, HH);
    format = format.replace(/%H/i, HH);
    format = format.replace(/%MM/i, MM);
    format = format.replace(/%m/i, MM);
    format = format.replace(/%SS/i, SS);
    format = format.replace(/%S/i, S);
    format = format.replace(/%b/i, shortMonthNames[m - 1]);
    format = format.replace(/%B/i, monthNames[m - 1]);

    return format;
}

function addComments(post_type, post_id) {
    fetch(`/api/v1/${post_type}/${post_id}/comments`)
        .then(result => result.json())
        .then(data => {
            let comments = data.comments.slice(5);
            let comments_block = document.querySelector(`#${post_type}-${post_id} .comments-block`)
            comments.forEach((comment) => {
                let score = 0;
                if (comment.score_data != null) {
                    score = comment.score_data * 1 + (!comment.score_data) * -1;
                }
                let created_at = new Date(comment.created_at)
                let raw_html = `<hr>
                <div class="comment row d-flex justify-content-center comment-vote pb-3"
                     id="comment-${comment.id}">
                    <div class="col-1">
                        <div class="comment-vote">
                            <div class="row">
                                <button class="${(score === 1) ? 'upvote ' : (score === -1) ? 'unclickable ' : ''}arrow-up" onclick="vote('comment', ${comment.id}, 'upvote'${(score === 1) ? ', true' : ''})">
                                    <svg class="svg-icon iconArrowUpLg"
                                         aria-hidden="true" width="18" height="18" viewBox="0 0 36 36">
                                        <path d="M2 26h32L18 10 2 26z"></path>
                                    </svg>
                                </button>
                            </div>
                    
                            <div class="row d-flex justify-content-center vote-count comment-vote">${comment.score}</div>
                    
                            <div class="row">
                                <button class="${(score === -1) ? 'downvote ' : (score === 1) ? 'unclickable ' : ''}arrow-down" onclick="vote('comment', ${comment.id}, 'downvote'${(score === -1) ? ', true' : ''})">
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
                              title="${created_at.format('%H:%M:%S %d.%m.%Y')}">– ${comment.author} ${created_at.format("%b %d '%y at %H:%M")}</span>
                    </div>
                </div>`
                comments_block.insertAdjacentHTML('beforeend', raw_html);
            })
            document.querySelector(`#${post_type}-${post_id} .comment-button-load`).remove()
        });
}

function vote(post_type, post_id, action, undo = false) {
    let undo_str = undo ? '/undo' : ''
    fetch(`/api/v1/${post_type}/${post_id}/${action}${undo_str}`,
        {method: 'POST'})
        .then(result => result.json())
        .then((data) => {
            if (data.success) {
                let upvoteButton = document.querySelector(`#${post_type}-${post_id} button.arrow-up`);
                let score_cnt = +document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML;
                let downvoteButton = document.querySelector(`#${post_type}-${post_id} button.arrow-down`);
                if (!undo) {
                    if (action === 'upvote') {
                        upvoteButton.classList.add('upvote')
                        let onclick = upvoteButton.getAttribute('onclick')
                        upvoteButton.setAttribute('onclick', onclick.slice(0, -1) + ', true)');
                        downvoteButton.classList.add('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = score_cnt + 1;
                    } else {
                        downvoteButton.classList.add('downvote')
                        let onclick = downvoteButton.getAttribute('onclick')
                        downvoteButton.setAttribute('onclick', onclick.slice(0, -1) + ', true)');
                        upvoteButton.classList.add('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = score_cnt - 1;
                    }
                } else {
                    if (action === 'upvote') {
                        upvoteButton.classList.remove('upvote')
                        let onclick = upvoteButton.getAttribute('onclick')
                        upvoteButton.setAttribute('onclick', onclick.slice(0, -7) + ')');
                        downvoteButton.classList.remove('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = score_cnt - 1;
                    } else {
                        downvoteButton.classList.remove('downvote')
                        let onclick = downvoteButton.getAttribute('onclick')
                        downvoteButton.setAttribute('onclick', onclick.slice(0, -7) + ')');
                        upvoteButton.classList.remove('unclickable')
                        document.querySelector(`#${post_type}-${post_id} div.vote-count`).innerHTML = score_cnt + 1;
                    }
                }
            }
        });

    return false;
}

function commentSendPreview(post_type, post_id) {
    let addButton = document.querySelector(`#${post_type}-${post_id} div.comment-button`);
    addButton.innerHTML =
        `<form name="create-comment" class="needs-validation" novalidate>
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
            <button type="submit" class="btn btn-primary button-send" onclick="commentPush('${post_type}', ${post_id})">Add comment</button>
        </div>  
    </div>
 </form>`;
}

function commentPush(post_type, post_id) {
    let commentForm = document.forms['create-comment'];
    let commentText = commentForm.elements.comment.value;
    let commentAuthor = commentForm.elements.name.value;
    if (!commentText || !commentAuthor) {
        return false
    }
    if (commentAuthor.length < 2 || commentAuthor.length > 64 || commentText.length < 3) {
        return false
    }
    commentForm.classList.add('was-validated');
    fetch(`/api/v1/${post_type}/${post_id}/comments/add`,
        {method: 'POST', body: `{"author": "${commentAuthor}", "body": "${commentText}"}`})
        .then(result => result.json())
        .then(() => window.location.reload());
    return false
}



