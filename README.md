# Draftsmith: Your Personal Knowledge Forge


<p><img src="./src/static/media/logo.png" style="float: left; width: 80px" /></p>



Draftsmith is an open-source, powerful note-taking and knowledge management system designed for thinkers, researchers, and lifelong learners. It's not just another note-taking app; it's your personal knowledge forge, helping you connect ideas, discover insights, and craft your thoughts with precision.

## 🌟 Key Features

- **Seamless Note Creation and Editing**: Quickly capture your thoughts and refine them with our intuitive Markdown editor.
- **Dynamic Knowledge Graph**: Visualize connections between your notes, uncovering relationships you never knew existed.
- **Backlinks and Forward Links**: Effortlessly navigate through your web of knowledge with bi-directional linking.
- **Powerful Search**: Find exactly what you're looking for with our advanced search capabilities.
- **Customizable Organization**: Structure your notes your way with a flexible hierarchical system.
- **Asset Management**: Easily upload and link to images, PDFs, and other files within your notes.
- **Responsive Design**: Access your knowledge base from any device, anytime.

## 🚀 Why Draftsmith?

In a world overflowing with information, Draftsmith stands out as your personal thinking environment. It's not just about storing information; it's about forging connections, sparking creativity, and building a second brain that evolves with you.

- **For Researchers**: Link hypotheses, track experiments, and uncover patterns in your data.
- **For Writers**: Organize your plots, characters, and world-building elements with ease.
- **For Students**: Connect concepts across subjects and build a personalized study guide.
- **For Professionals**: Manage projects, track ideas, and never lose an important thought again.

## 🛠 Getting Started

1. Clone the repository:
   ```
   mkdir /opt/draftsmith-flask
   cd /opt/draftsmith-flask
   git clone https://github.com/RyanGreenup/draftsmith_flask

   ```
2. Install dependencies:
   ```
   poetry install
   ```
3. Run the application:
   ```
   poetry run python src/main.py
   ```
4. Open your browser and navigate to `http://localhost:8080`

For better performance consider using a production server like `gunicorn` or `uwsgi`. See the Docker container provided in the [API Setup Guide](https://ryangreenup.github.io/draftsmith_api/installation.html) which includes this pre-packaged.

### Backend

Install the backend API by following the [API Setup Guide](https://ryangreenup.github.io/draftsmith_api/installation.html), this is essentially a `docker compose up` command.

### Interfaces

2. **CLI Client**
   - Install Python and dependencies.
       - `pipx install git+https://github.com/RyanGreenup/draftsmith_cli --force`

3. [**PyQt GUI**](https://github.com/RyanGreenup/draftsmith)
   - `pipx install git+https://github.com/RyanGreenup/draftsmith`

## 🤝 Contributing

We believe in the power of community-driven development. Whether you're fixing bugs, adding new features, or improving documentation, your contributions are welcome!

Check out our [Contribution Guidelines](CONTRIBUTING.md) to get started.

## 📜 License

Draftsmith is open-source software licensed under the MIT license. See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgements

A big thank you to all our contributors and the open-source community for making Draftsmith possible.

---

Start forging your knowledge today with Draftsmith. Your ideas deserve a home as unique as they are.
