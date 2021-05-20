class CreateThread extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            nameValue: '',
            titleValue: '',
            descriptionValue: '',
            tagsValue: ''
        }

        this.nameChange = this.nameChange.bind(this);
        this.titleChange = this.titleChange.bind(this);
        this.descriptionChange = this.descriptionChange.bind(this);
        this.tagsChange = this.tagsChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    questionPush(name, title, text, tags) {
        console.log(`${name} ${title} ${text} ${tags}`)
        fetch('http://shitoverflow.tmweb.ru/api/v1/questions/add', {
            method: 'POST',
            headers: { 'Content-Type': 'CreateThread/json' },
            body: `{"author": "${name}", "title": "${title}", "body": "${text}", "tags ": "${tags}"}`})
            .then(result => result.json())
            .then(question => window.location.href = `http://shitoverflow.tmweb.ru/questions/${question.id}`);
    }

    invalidChecker(element) {
        let elementClassList = element.classList.toString().split(" ");
        return elementClassList.indexOf('is-invalid') === -1;
    }

    nonNulInputChecker(event, className) {
        let element = document.querySelector(className);
        let elementClassList = element.classList.toString().split(" ");
        if (elementClassList.indexOf('is-invalid') !== -1) {
            if (event.target.value.length > 0) {
                element.classList.remove('is-invalid');
            }
        } else {
            if (event.target.value.length === 0) {
                element.classList.add('is-invalid');
            }
        }
    }

    nameChange(event) {
        let nameInput = document.querySelector('.name-input');
        let nameInputClassList = nameInput.classList.toString().split(" ");
        if (nameInputClassList.indexOf('is-invalid') !== -1) {
            if (event.target.value.length >= 3) {
                nameInput.classList.remove('is-invalid');
            }
        } else {
            if (event.target.value.length < 3) {
                nameInput.classList.add('is-invalid');
            }
        }

        this.setState({nameValue: event.target.value});
    }

    titleChange(event) {
        this.nonNulInputChecker(event, '.title-input');
        this.setState({titleValue: event.target.value});
    }

    descriptionChange(event) {
        this.nonNulInputChecker(event, '.description-input')
        this.setState({descriptionValue: event.target.value});
    }

    tagsChange(event) {
        this.setState({tagsValue: event.target.value});
    }

    handleSubmit(event) {
        let nameInput = document.querySelector('.name-input');
        let titleInput = document.querySelector('.title-input');
        let descriptionInput = document.querySelector('.description-input');

        this.validationInputs(nameInput, titleInput, descriptionInput);

        console.log(this.invalidChecker(nameInput) && this.invalidChecker(titleInput) && this.invalidChecker(descriptionInput))

        if (this.invalidChecker(nameInput) && this.invalidChecker(titleInput) && this.invalidChecker(descriptionInput)) {
            this.questionPush(this.state.nameValue, this.state.titleValue, this.state.descriptionValue, this.state.tagsValue);
        }

        event.preventDefault();
    }

    validationInputs(nameInput, titleInput, descriptionInput) {
        if (3 > this.state.nameValue.length || this.state.nameValue.length > 64) {
            nameInput.classList.add('is-invalid');
        }

        if (this.state.titleValue.length === 0) {
            titleInput.classList.add('is-invalid');
        }

        if (this.state.descriptionValue.length === 0) {
            descriptionInput.classList.add('is-invalid');
        }
    }

    render() {
        return (
            <form name="create" className="create-form" novalidate onSubmit={this.handleSubmit}>
                <div className="mb-3 form-row">
                    <label htmlFor="nameField">Name</label>
                    <input name="name" type="text" className="form-control name-input" id="nameField"
                           value={this.state.nameValue} onChange={this.nameChange} placeholder='billgates'/>
                    <div className="invalid-feedback">Please choose your name (3-64 symbols)</div>

                </div>
                <div className="mb-3 form-row">
                    <label htmlFor="titleField">Title</label>
                    <input name="title" type="text" className="form-control title-input" id="titleField "
                           placeholder="e.g How to patch KDE2 for FreeBSD" value={this.state.titleValue}
                           onChange={this.titleChange}/>
                    <div className="invalid-feedback">Please input title</div>
                </div>
                <div className="mb-3 form-group">
                    <label htmlFor="descriptionField">Description</label>
                    <textarea name="body" className="form-control description-input" id="descriptionField" rows="4"
                              value={this.state.descriptionValue} onChange={this.descriptionChange}/>
                    <div className="invalid-feedback">Please specify question</div>
                </div>
                <div className="mb-3 form-row">
                    <label htmlFor="tagsField">Tags</label>
                    <input name="tags" type="text" className="form-control" id="tagsField"
                           placeholder="python hello-world" value={this.state.tagsValue}
                           onChange={this.tagsChange}/>
                </div>

                <button type="submit" className="btn btn-primary">Post your question</button>
            </form>
        );
    }
}
