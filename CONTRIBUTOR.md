 # Contributing to Retuve

 We welcome contributions to Retuve! Whether it's bug reports, feature requests, code contributions, or documentation improvements, your help is greatly appreciated.

 ## How to Contribute

 1.  **Fork the Repository:** Start by forking the Retuve repository to your own GitHub account.
 2.  **Create a Branch:** Create a new branch for your changes. Use a descriptive name, like `fix-typo` or `add-new-feature`.
 3.  **Make Changes:** Implement your changes, following the project's coding style and guidelines.
 4.  **Test Your Changes:** Ensure that your changes don't introduce any regressions and that all tests pass. Add new tests if necessary.
 5.  **Commit Your Changes:** Commit your changes with a clear and concise commit message.
 6.  **Push to Your Fork:** Push your branch to your forked repository.
 7.  **Create a Pull Request:** Submit a pull request to the main Retuve repository. Provide a detailed description of your changes and their impact.


 ## Code Style

 *   Follow the existing code style.
 *   Write clear and concise code.
 *   Add comments where necessary to explain complex logic.
 *   Keep functions and classes short and focused.


 ## Bug Reports

 If you encounter a bug, please submit a detailed bug report, including:

 *   A clear and descriptive title.
 *   Steps to reproduce the bug.
 *   The expected behavior.
 *   The actual behavior.
 *   Your environment (operating system, Python version, etc.).

 ## Feature Requests

 If you have a feature request, please submit it as an issue, including:

 *   A clear and descriptive title.
 *   A detailed description of the feature.
 *   The use cases it would address.
 *   Any potential drawbacks.


 ## Documentation

 Documentation improvements are always welcome. If you find errors or omissions in the documentation, please submit a pull request with corrections.


 ## Versioning

 Retuve uses a `x.y.z` versioning system, but with a slightly different interpretation:

 *   `z`: This version number will be incremented frequently for small changes, bug fixes, and minor improvements.
 *   `y`: This version number will be incremented when the `poe testgen` command creates a new [changenote](https://github.com/radoss-org/retuve/tree/main/changenotes), indicating that the project's metrics have changed significantly.  This represents a meaningful update to the project's core functionality or performance.
 *   `x`: This version number is reserved for large, breaking changes to the API or core architecture of Retuve.

 This is done to better match with the version intuition of the people using Retuve - where code changes matter less than medical changes.


 **Important: Pre-v1.0.0 Releases**

 Please note that until Retuve reaches version 1.0.0, significant and potentially breaking changes are possible in any release. The versioning scheme should be followed, but it is important to understand that the project is still evolving rapidly.

 ## Thank You

 Thank you for contributing to Retuve!
