package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"net/http"
	"os"

	_ "github.com/go-sql-driver/mysql"
)

var db_user = os.Getenv("vivadb_user")
var db_server = os.Getenv("vivadb_server")
var db_pass = os.Getenv("vivadb_pass")

type Details struct {
	Title       string
	Description string
	Author      string
}

type Results struct {
	Id    int `json:"id"`
	Url   string
	Lat   float64
	Lon   float64
	Preco float64
}

type DataTemplate struct {
	Details Details
	Results []Results
}

var ts *template.Template

func main() {

	ts = template.Must(template.ParseGlob("*.html"))
	mux := http.NewServeMux()
	// fs := http.FileServer(http.Dir("."))
	mux.HandleFunc("/", pageHandler)
	http.ListenAndServe(":3131", mux)
}

func getImoveis() []Results {
	fmt.Println("mysql", db_user+":"+db_pass+"@tcp("+db_server+":3306)/viva_real")
	db, err := sql.Open("mysql", db_user+":"+db_pass+"@tcp("+db_server+":3306)/viva_real")
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()
	query := `SELECT i.id,
				url,
				CAST(lat AS FLOAT),
				CAST(lon AS FLOAT),
				p.preco
			FROM imoveis i
			LEFT JOIN precos p ON p.id_imovel = i.id  
			WHERE lat IS NOT NULL AND lon IS NOT NULL
			AND lat != '' AND lon != ""
			LIMIT 10`

	results, err := db.Query(query)
	if err != nil {
		panic(err.Error())
	}
	var results_slice []Results
	for results.Next() {
		var res Results
		err = results.Scan(&res.Id,
			&res.Url,
			&res.Lat,
			&res.Lon,
			&res.Preco,
		)
		if err != nil {
			panic(err.Error())
		}
		results_slice = append(results_slice, res)
	}
	return results_slice
}

func pageHandler(w http.ResponseWriter, r *http.Request) {
	// fmt.Fprint(w, "Hello, Word!")
	results := getImoveis()
	details := Details{"Viva Real Map", "consultando imoveis no Gmaps", "Luiz Vieira"}
	data := DataTemplate{details, results}
	ts.ExecuteTemplate(w, "index.html", data)
}
