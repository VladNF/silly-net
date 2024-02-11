echo "Migrations BEFORE rollback command"
yoyo list
yoyo rollback -r $(ROLLBACK_REVISION)
echo "Migrations AFTER rollback command"
yoyo list