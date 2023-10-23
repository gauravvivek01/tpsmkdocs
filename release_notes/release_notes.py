#!/usr/bin/python3
import argparse
import subprocess
import sys
import os
import tempfile
import shutil

class releaseNotes:
    HEADING="Release Name Text"
    previous_releases="Previous Release History"
    LOCATION_TEXT="This release is available in"
    NIGHTLY_LOCATION="\\\\10.211.128.208\\tftpboot\\work\\Emerald_Releases"
    FUNCTIONALITY_HEADING="New functionality added/updated"
    KNOWNISSUES_HEADING="Known Issues in this Release"
    RESTRICTIONS="Restrictions"

    @staticmethod
    def getJIRAData(version):
        version_number="EMD-{}".format(version)
        script_name="./ask-jira/query-bug-filter.sh"
        jira_filter='project = BUG AND fixVersion in ({}) AND Status in (Resolved) AND Product[Dropdown] = Appliance-SW ORDER BY key DESC'.format(version_number)
        args = ("sshpass", "-p", "cloud$1", "ssh", "-o", "StrictHostKeyChecking=no", "developer@10.211.129.241", "{} '{}'".format(script_name, jira_filter) )
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        return str(output, 'utf-8').splitlines()

    @staticmethod
    def printResolvedTable(fileHandle, convert):
        fileHandle.writelines("### Issues resolved in this Release\n\n")
        fileHandle.writelines("|***Key***|***Summary***|\n")
        fileHandle.writelines("|-----|---------|\n")
        for line in convert:
            mark1 = line.find('*') + 2
            mark2 = line.find(':')
            bugNum = line[mark1:mark2]
            bugText = line[mark2+1:]
            bugURL = "https://bboxjira.atlassian.net/browse/" + bugNum
            fileHandle.writelines("|[{}]({})|{}|\n".format(bugNum, bugURL, bugText.strip()))
        fileHandle.writelines("\n")

    @staticmethod
    def printReleaseTable(fileHandle, releaseList):
        fileHandle.writelines("### {}\n".format(previous_releases))
        fileHandle.writelines("|***Release Number***|***Summary***|")
        fileHandle.writelines("|-----|---------|")
        for release in releaseList:
            fileHandle.writelines("|{}||".format(release))
        fileHandle.writelines("")

    def printToFile(self, fileHandle):
        fileHandle.writelines("# {}\n\n".format(self.HEADING))
        #printReleaseTable(release_list)
        fileHandle.writelines("## {} ECX/RCX\n\n".format(self.full_version))
        fileHandle.writelines("{} {}\n\n".format(self.LOCATION_TEXT, self.NIGHTLY_LOCATION))
        fileHandle.writelines("Source branch: {}\n\n".format(self.branch))

        fileHandle.writelines(("### {}\n\n".format(self.FUNCTIONALITY_HEADING)))
        fileHandle.writelines(("* N/A\n\n"))

        fileHandle.writelines(("### {}\n\n".format(self.KNOWNISSUES_HEADING)))
        fileHandle.writelines(("* N/A\n\n"))

        fileHandle.writelines(("### {}\n\n".format(self.RESTRICTIONS)))
        fileHandle.writelines(("* N/A\n\n"))

        bug_list = self.getJIRAData(self.version_num)
        self.printResolvedTable(fileHandle, bug_list)

    def createReleaseNotes(self):
        release_file="{}".format("./V{}_RELEASE_NOTES.md".format(self.version_num.replace('.', '_')))
        exists = os.path.exists(release_file)
        temp_file=tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        self.printToFile(temp_file)

        if exists:
            print("Revision of release note already exits, appending new data")
            #Copy in the current release notes
            temp_file.writelines("___\n")
            with open(release_file) as current_release:
                #Skip the first line as it is the previous heading
                next(current_release)
                for line in current_release:
                    temp_file.writelines(line)
        temp_file.close()
        shutil.move(temp_file.name, release_file)
        os.system("chmod ugo+rwx {}".format(release_file))
    
    def checkVersionFormat(self, version):
        if 'V' in version:
            return False
        if "_r" not in version:
            return False
        return True
    
    def __init__(self, full_version, branch):
        self.branch = branch
        if not self.checkVersionFormat(full_version):
            print("Error {} format is incorrect expected input is X.X.X_rXXXXX".format(args.version))
            exit(1)
        self.full_version = full_version
        self.version_num = full_version[:full_version.find('_')]

parser = argparse.ArgumentParser(description='Script to create or append Release notes')
parser.add_argument('-b', '--branch', dest='branch', required=True, help='Branch the build belongs to')
parser.add_argument('-v', '--version', dest='version', required=True, help='Full Version Number in the format X.X.X_rXXXXX')
args = parser.parse_args()

notes=releaseNotes(args.version, args.branch)
notes.createReleaseNotes()
