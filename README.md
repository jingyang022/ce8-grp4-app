# CE8-Group4 Application Repository

1. This repo stores the image code for the container.

2. The CICD workflow does the following:
 - build and push the image to the AWS ECR.
 - checks the code for vulnerabilities.
 - Update the task definition of the container and deploy a new one.

3. The developer will create a dev branch and work on it. Any new features will require a Pull Request to be reviewed and approved before it can be merged into the main branch.

4. The infrastructure code and documentation is available at the [Main Project Repository](https://github.com/jingyang022/ce8-grp4-infra)
