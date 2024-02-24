echo "Migrations BEFORE rollback command"
yoyo list
echo "Rollback revision $ROLLBACK_REVISION"
yoyo rollback -r $ROLLBACK_REVISION
echo "Migrations AFTER rollback command"
yoyo list