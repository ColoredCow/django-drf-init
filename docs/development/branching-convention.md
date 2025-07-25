## Branch Naming Convention

## Quick Legend
<table>
  <thead>
    <tr>
      <th>Branch Type</th>
      <th>Branch</th>
      <th>Description, Instructions, Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Code Flow</td>
      <td>main</td>
      <td>This is the main branch for production.</td>
    </tr>
    <tr>
      <td>Temporary</td>
      <td>feature</td>
      <td>Base branch should always be dev.</td>
    </tr>
    <tr>
      <td></td>
      <td>bugfix</td>
      <td>Base branch should always be dev.</td>
    </tr>
    <tr>
      <td></td>
      <td>hotfix</td>
      <td>Base branch should be main.</td>
    </tr>
    <tr>
      <td></td>
      <td>doc</td>
      <td>Base branch should always be dev.</td>
    </tr>
  </tbody>
</table>

## Branching

In any software, every day many branches are created and pushed to the GitHub repository. Having a manageable code repository is important and mandatory when working with a team.

The application development uses branch naming conventions to work with git repositories. In this convention, the branches are divided into two categories:

### Code Flow Branches
These branches which we expect to be permanently available on the repository follow the flow of code changes starting from development until the production.


#### 1. main
This is the main branch for production. Nothing should be directly pushed into this branch except for the hot-fix errors and the dev branch after the complete testing of the issues or bug fixes.
