module.exports = {
  entry: {
    dev: "./src/index.tsx",
  },
  output: {
    filename: "./build/index.js",
  },
  devtool: "source-map",
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
  },
  module: {
    loaders: [
      // Typescript
      { test: /\.tsx?$/, loader: "ts-loader" },
    ],
  },
};
