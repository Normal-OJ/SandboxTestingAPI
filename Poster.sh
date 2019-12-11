Post(){
	curl -X POST -H "Content-Type: application/json" -d "$1" "$2"
}
Post '{"yee":12}' "http://127.0.0.1:6666/submission/C_abFileRead"
