# Taxonomy Editor Frontend

This is the main user interface developed in React, which works in conjunction with the Taxonomy Editor API.

## Requirements

- [Node](https://nodejs.org/en/)
- [npm](https://www.npmjs.com/)

## Libraries

- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [iso-639-1](https://www.npmjs.com/package/iso-639-1)

This project was initially setup using [Create React App](https://github.com/facebook/create-react-app), [the documentation](https://create-react-app.dev/) might be useful.

## Setup Dev Environment

See [this guide](../doc/introduction/setup-dev.md) for more information.

For frontend code formatting, we added [Prettier and Husky](https://prettier.io/docs/en/precommit.html), these tools will automatically format your files on every commit. In case you want to use them you need to locally install the frontend dependencies and have [node and npm](https://nodejs.org/es/) in you computer.

```bash
cd taxonomy-editor-frontend
npm i
```

## Check it!

The frontend should be available at the URL `http://ui.taxonomy.localhost:8091`.

You should be able to view the homepage of Taxonomy Editor.
