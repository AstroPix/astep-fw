set ::icflowDocFolder [file normalize [file dirname [info script]]]
package ifneeded icflow.doc 1.0 {

    package provide icflow.doc 1.0
    package require icflow

    icDefineParameter DOCS_WORKFOLDER "DOCS Workfolder" .icflow/doc

    #set icflowDocFolder [file dirname [info script]]
    #set icflowDocFolder [file normalize [file dirname [info script]]]
    #puts "Icflow Doc: $::icflowDocFolder"


    ## Utils
    #################
    namespace eval icdoc {
        set workFolder .icflow/doc

        proc setup args {
            set currentFolder [pwd]
            set setupFolder $currentFolder/$::icdoc::workFolder
            exec mkdir -p $setupFolder 
            foreach toCopy [glob -nocomplain $::icflowDocFolder/mkdocs/*] {
                file delete -force $setupFolder/[file tail $toCopy]
                file copy -force -- $toCopy $setupFolder
            }

            #exec cp -Rf $::icflowDocFolder/mkdocs/* $currentFolder/.icflow
            try {
                ## Setup mkdocs
                cd $setupFolder
                exec make setup >@stdout 2>@ stdout

                ## Prepare docs files
                if {![file exists docs]} {
                    exec rm -f docs
                    exec ln -s $currentFolder/docs docs
                }

                ## Copy work stuff in docs
                file delete -force docs/_icflow_work_

                foreach folder [list stylesheets images] {

                    exec mkdir -p docs/_icflow_work_/$folder
                    file delete -force docs/_icflow_work_/$folder
                    file copy -force -- $::icflowDocFolder/mkdocs/$folder docs/_icflow_work_/
                }

                #cd docs 
                ## Copy Documentation files 
                #foreach toCopy [concat [glob -nocomplain $currentFolder/*.md] [glob -nocomplain -types d $currentFolder/*]] {
                #    file copy -force --  $toCopy .
                #}
                #cd ..
            } finally {
                cd $currentFolder
            }
        }
    }

    ## Generate
    #########


    proc icProduceDoc args {
        
        set makeArgs {}
        if {[lsearch $::argv --update]!=-1} {
            lappend makeArgs -B
        }

        ##  If there is a mkdocs.yml in the docs/ folder, we just start mkdocs as is
        if {[file exists docs/mkdocs.yml]} {

            cd docs
            if {[lsearch $::argv --serve]!=-1} {
                exec make {*}$makeArgs -f $::env(DOCSV1_HOME)/mkdocs/Makefile serve >@stdout 2>@stdout
            } else {
                set cmd [list {*}$makeArgs -f $::env(DOCSV1_HOME)/mkdocs/Makefile generate]
                exec make {*}$cmd >@stdout 2>@stdout
            }

        } elseif  {[file exists mkdocs.yml]} {
            if {[lsearch $::argv --serve]!=-1} {
                exec make $makeArgs -f $::env(DOCSV1_HOME)/mkdocs/Makefile serve >@stdout 2>@stdout
            } else {
                exec make $makeArgs -f $::env(DOCSV1_HOME)/mkdocs/Makefile generate >@stdout 2>@stdout
            }
        } else {

            ::icdoc::setup
            cd $::DOCS_WORKFOLDER
            puts "Producing docs from [pwd]"
            if {[lsearch $::argv --serve]!=-1} {
                exec make -f $::env(DOCSV1_HOME)/mkdocs/Makefile serve >@stdout 2>@ stdout
            } else {
                exec make -f $::env(DOCSV1_HOME)/mkdocs/Makefile generate >@stdout 2>@ stdout
            }
            #::icdoc::setup

            #set currentFolder [pwd]
            #set setupFolder $currentFolder/$::icdoc::workFolder
            #icInfo "Generating Documentation in $currentFolder, args: $::argv"

            #try {
            #    cd $setupFolder
            #    if {[lsearch $::argv --serve]!=-1} {
            #        exec make serve >@stdout 2>@ stdout
            #    } else {
            #        exec make generate >@stdout 2>@ stdout
            #    }
            #    
            #} finally {
            #    cd $currentFolder
            #}
        }

        
        #cd $currentFolder/.icflow && make setup
    }


}