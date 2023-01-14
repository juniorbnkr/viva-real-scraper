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
	Id      int `json:"id"`
	Url     string
	Lat     float64
	Lon     float64
	Preco   float64
	Area    string
	Quartos int
	Foto    string
}

type DataTemplate struct {
	Details Details
	Results []Results
	Slct    string
}

var ts *template.Template
var default_query string = `SELECT i.id,
			MIN(url),
			CAST(MIN(lat) AS FLOAT) as lat,
			CAST(MIN(lon) as FLOAT) as lon, 
			MIN(p.preco)  + MIN(p.condominio)  as preco,
			MIN(i.area) as area,
			MIN(i.quartos) as quartos,
			MIN(COALESCE(f.link,'')) as foto 
		FROM imoveis i
		LEFT JOIN precos p ON p.id_imovel = i.id 
		LEFT JOIN fotos f ON f.id_imovel = i.id
		WHERE lat IS NOT NULL AND lon IS NOT NULL 
		AND lat != '' AND lon != "" #Editar a partir daqui
		GROUP BY i.id
		LIMIT 300`

func main() {

	ts = template.Must(template.ParseGlob("*.html"))
	mux := http.NewServeMux()
	// fs := http.FileServer(http.Dir("."))
	mux.HandleFunc("/", pageHandler)
	fmt.Println("Server Inicializado")
	http.ListenAndServe(":3131", mux)
}

func getImoveis(method string, slct string) []Results {
	fmt.Println("Using: mysql", db_user+":"+db_pass+"@tcp("+db_server+":3306)/viva_real")
	db, err := sql.Open("mysql", db_user+":"+db_pass+"@tcp("+db_server+":3306)/viva_real")
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()
	var query string
	switch method {
	case "GET":
		query = default_query
	case "POST":
		query = slct
	}

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
			&res.Area,
			&res.Quartos,
			&res.Foto,
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
	fmt.Println("Request using " + r.Method)
	if r.URL.Path != "/" {
		fmt.Println("URL path invalid: " + r.URL.Path)
		http.Error(w, "404 not found.", http.StatusNotFound)
		return
	}
	results := getImoveis(r.Method, r.FormValue("select"))
	details := Details{"Viva Real Map", "consultando imoveis no Gmaps", "Luiz Vieira"}
	var textarea string
	if r.FormValue("select") == "" {
		textarea = default_query
	} else {
		textarea = r.FormValue("select")
	}
	data := DataTemplate{details, results, textarea}
	ts.ExecuteTemplate(w, "index.html", data)
}
