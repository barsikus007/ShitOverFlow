import React from "react";


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

    nameChange(event) {
        this.setState({nameValue: event.target.value});
    }

    titleChange(event) {
        this.setState({titleValue: event.target.value});
    }

    descriptionChange(event) {
        this.setState({descriptionValue: event.target.value});
    }

    tagsChange(event) {
        this.setState({tagsValue: event.target.value});
    }

    handleSubmit(event) {
        alert("test");
        this.validationInputs(event, this.state.nameValue, this.state.titleValue, this.state.descriptionValue);
        event.preventDefault();
    }

    validationInputs(event, username, title, description) {
        if (3 > username.length || username.length > 64) {
            let invalidNameMsg = document.querySelector('.invalid-name-form');
            invalidNameMsg.classList.add('d-block');
        }
    }

    render() {
        return (
            <div className="bg-light border rounded p-3 row g-0">
                <form className="needs-validation" name="create" onSubmit={this.handleSubmit}>
                    <div className="mb-3 form-row">
                        <label htmlFor="nameField">Name</label>
                        <input name="name" type="text" className="form-control input-name" id="nameField"
                               value={this.state.nameValue} onChange={this.nameChange} required/>
                        <div className="invalid-feedback invalid-name-form">Please choose your name (3-64 symbols)</div>
                    </div>
                    <div className="mb-3 form-row">
                        <label htmlFor="titleField">Title</label>
                        <input name="title" type="text" className="form-control" id="titleField"
                               placeholder="e.g How to patch KDE2 for FreeBSD" value={this.state.titleValue}
                               onChange={this.titleChange} required/>
                        <div className="invalid-feedback invalid-title-form">Please input title</div>
                    </div>
                    <div className="mb-3 form-group">
                        <label htmlFor="descriptionField">Description</label>
                        <textarea name="body" className="form-control" id="descriptionField" rows="4"
                                  value={this.state.descriptionValue} onChange={this.descriptionChange} required/>
                        <div className="invalid-feedback invalid-description-form">Please specify question</div>
                    </div>
                    <div className="mb-3 form-row">
                        <label htmlFor="tagsField">Tags</label>
                        <input name="tags" type="text" className="form-control" id="tagsField"
                               placeholder="python hello-world" value={this.state.tagsValue}
                               onChange={this.tagsChange}/>
                    </div>

                    <button type="submit" className="btn btn-primary">Post your question</button>
                </form>
            </div>);
    }
}

export default CreateThread;