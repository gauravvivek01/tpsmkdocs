#!/usr/bin/python3
import argparse
import subprocess
import sys
import os
import tempfile
import shutil


class releaseNotes:
    HEADING = "Release Name Text"
    previous_releases = "Previous Release History"
    LOCATION_TEXT = "This release is available in"
    NIGHTLY_LOCATION = "\\\\10.211.128.208\\tftpboot\\work\\Deskvue_Release"
    FUNCTIONALITY_HEADING = "New functionality added/updated"
    KNOWNISSUES_HEADING = "Known Issues in this Release"
    RESTRICTIONS = "Restrictions"

    @staticmethod
    def getJIRADataResolved(version):
        version_number = "{}".format(version)
        script_name = "./ask-jira/query-bug-filter.sh"
        jira_filter = 'project = BUG AND fixVersion in (\"{}\") AND Status in (Resolved) AND \"Severity[Dropdown]\" != Enhancement AND Product[Dropdown] = SDKVM ORDER BY key DESC'.format(
            version_number)
        print(jira_filter)
        args = ("sshpass", "-p", "cloud$1", "ssh", "-o", "StrictHostKeyChecking=no",
                "developer@10.211.129.241", "{} '{}'".format(script_name, jira_filter))
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        if output is not None:
            data = str(output, 'utf-8').splitlines()
        else:
            data = ""
            # "Error retrieving data: {}".format{output}
            print("Error retrieving data for " + output)
        return data

    @staticmethod
    def getJIRADataVerified(version):
        version_number = "{}".format(version)
        script_name = "./ask-jira/query-bug-filter.sh"
        jira_filter = 'project = BUG AND fixVersion in (\"{}\") AND Status in (\"To Be Verified\") AND \"Severity[Dropdown]\" != Enhancement AND Product[Dropdown] = SDKVM ORDER BY key DESC'.format(
            version_number)
        print(jira_filter)
        args = ("sshpass", "-p", "cloud$1", "ssh", "-o", "StrictHostKeyChecking=no",
                "developer@10.211.129.241", "{} '{}'".format(script_name, jira_filter))
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        return str(output, 'utf-8').splitlines()

    @staticmethod
    def getJIRADataOpen(version):
        version_number = "{}".format(version)
        script_name = "./ask-jira/query-bug-filter.sh"
        jira_filter = 'project = BUG AND fixVersion in (\"{}\") AND Status not in (\"To Be Verified\",\"Resolved\",\"Closed\",\"retest\") AND \"Severity[Dropdown]\" != Enhancement AND Product[Dropdown] = SDKVM ORDER BY key DESC'.format(
            version_number)
        print(jira_filter)
        args = ("sshpass", "-p", "cloud$1", "ssh", "-o", "StrictHostKeyChecking=no",
                "developer@10.211.129.241", "{} '{}'".format(script_name, jira_filter))
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
            fileHandle.writelines("|[{}]({})|{}|\n".format(
                bugNum, bugURL, bugText.strip()))
        fileHandle.writelines("\n")

    @staticmethod
    def printToBeVerifiedTable(fileHandle, convert):
        fileHandle.writelines("### Issues to be verified in this Release\n\n")
        fileHandle.writelines("|***Key***|***Summary***|\n")
        fileHandle.writelines("|-----|---------|\n")
        for line in convert:
            mark1 = line.find('*') + 2
            mark2 = line.find(':')
            bugNum = line[mark1:mark2]
            bugText = line[mark2+1:]
            bugURL = "https://bboxjira.atlassian.net/browse/" + bugNum
            fileHandle.writelines("|[{}]({})|{}|\n".format(
                bugNum, bugURL, bugText.strip()))
        fileHandle.writelines("\n")

    @staticmethod
    def printOpenTable(fileHandle, convert):
        fileHandle.writelines("### Issues unresolved in this Release\n\n")
        fileHandle.writelines("|***Key***|***Summary***|\n")
        fileHandle.writelines("|-----|---------|\n")
        for line in convert:
            mark1 = line.find('*') + 2
            mark2 = line.find(':')
            bugNum = line[mark1:mark2]
            bugText = line[mark2+1:]
            bugURL = "https://bboxjira.atlassian.net/browse/" + bugNum
            fileHandle.writelines("|[{}]({})|{}|\n".format(
                bugNum, bugURL, bugText.strip()))
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
        # printReleaseTable(release_list)
        fileHandle.writelines("## {} \n\n".format(self.full_version))
        fileHandle.writelines("{} {}\n\n".format(
            self.LOCATION_TEXT, self.NIGHTLY_LOCATION))
        fileHandle.writelines("Source branch: {}\n\n".format(self.branch))

        fileHandle.writelines(
            ("### {}\n\n".format(self.FUNCTIONALITY_HEADING)))
        fileHandle.writelines(("* N/A\n\n"))

        fileHandle.writelines(("### {}\n\n".format(self.KNOWNISSUES_HEADING)))
        fileHandle.writelines(("* N/A\n\n"))

        fileHandle.writelines(("### {}\n\n".format(self.RESTRICTIONS)))
        fileHandle.writelines(("* N/A\n\n"))

        resolved_bug_list = self.getJIRADataResolved(self.version_num)
        self.printResolvedTable(fileHandle, resolved_bug_list)

        tbv_bug_list = self.getJIRADataVerified(self.version_num)
        self.printToBeVerifiedTable(fileHandle, tbv_bug_list)

        open_bug_list = self.getJIRADataOpen(self.version_num)
        self.printOpenTable(fileHandle, open_bug_list)

    def createReleaseNotes(self):
        release_file = "{}".format(
            "./{}_RELEASE_NOTES.md".format(self.version_num.replace('.', '_')))
        release_file = release_file.replace(' ', '_')
        exists = os.path.exists(release_file)
        temp_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        self.printToFile(temp_file)

        if exists:
            print(
                "Revision of release note: " + release_file + " already exits, appending new data")
            # Copy in the current release notes
            temp_file.writelines("___\n")
            with open(release_file) as current_release:
                # Skip the first line as it is the previous heading
                next(current_release)
                for line in current_release:
                    temp_file.writelines(line)
        temp_file.close()
        shutil.move(temp_file.name, release_file)
        os.system("chmod ugo+rwx {}".format(release_file))

    def checkVersionFormat(self, version):
        if "SDKVM" not in version:
            return False
        if "_r" not in version:
            return False
        return True

    def __init__(self, full_version, branch):
        self.branch = branch
        if not self.checkVersionFormat(full_version):
            print("Error {} format is incorrect expected input is SDKVM x.x.x_rx".format(
                args["version"]))
            exit(1)
        self.full_version = full_version
        self.version_num = full_version[:full_version.find('_')]


# parser = argparse.ArgumentParser(
#     description='Script to create or append Release notes')
# parser.add_argument('-b', '--branch', dest='branch',
#                     required=True, help='Branch the build belongs to')
# parser.add_argument('-v', '--version', dest='version', required=True,
#                     help='Full Version Number in the format X.X.X_rXXXXX')
# args = parser.parse_args()
args = {'version':  "", 'branch':  ""}
args["version"] = "SDKVM 1.2.0_r105"
args["branch"] = "main"
notes = releaseNotes(args["version"], args["branch"])
notes.createReleaseNotes()
