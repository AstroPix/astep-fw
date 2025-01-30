package require icflow 


icInfo "Updating ICFlow from CI"

## Find all icflow_ installation folders, if one is a git one, update

## Update from CI 
exec wget http://ipe-iperic-srv1.ipe.kit.edu/gitlab/api/v4/projects/51/jobs/artifacts/main/download?job=package-job -O icflow_latest.zip >@ stdout 2>@ stdout

## Get Name of file 
set icflowReleaseFileName [lindex [split [exec unzip -lqq icflow_latest.zip] " "] end]
set icflowReleaseName [lindex [split $icflowReleaseFileName .] 0]
icInfo "ICFlow Release Name: $icflowReleaseName"

## If already exists, don't update
proc doInstall args {
    icInfo "Decompressing Release archive"
    exec unzip icflow_latest.zip >@ stdout 2>@ stdout
    exec tar xvaf $::icflowReleaseFileName >@ stdout 2>@ stdout
}
if {[file exists $icflowReleaseName]} {
    icWarn "ICFlow Release seems installed already"
    puts "Do you want to overwrite the installation \[y/N\] (default=N)?" 
    set answer [read stdin 1]
    if {$answer=="y"} {
        icWarn "Replacing existing installation"

        set backupTarget "${icflowReleaseName}.backup.[exec date +%s].tar.gz"
        icWarn "Backing up current installation to: $backupTarget"
        exec tar cvfz ${backupTarget} $::icflowReleaseName/ >@ stdout 2>@ stdout

        icWarn "Deleting...."
        file delete -force $icflowReleaseName
        doInstall

    } else {
        icWarn "Not doing anything (user answer: $answer)"
    }
} else {
    doInstall
}

