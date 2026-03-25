Set-Location c:\Dev\PyAgent
$existing = git branch --list "prj0000058-mobile-responsive-nebula-os"
if ($existing) {
    git checkout prj0000058-mobile-responsive-nebula-os
    $r = "checkout-existing"
} else {
    git checkout -b prj0000058-mobile-responsive-nebula-os
    $r = "created-new"
}
$branch = git rev-parse --abbrev-ref HEAD
Set-Content "c:\Dev\PyAgent\_branch_result.txt" "RESULT=$r BRANCH=$branch"
