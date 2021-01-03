import React from "react";
import Table from "react-bootstrap/Table";
import Spinner from "react-bootstrap/Spinner";
import "bootstrap/dist/css/bootstrap.min.css";
import AdaptiveTable from "./AdaptiveTable";


class myComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rowData: [],
      txns : [],
      selectedRow : "",
      loading : true
    };
  }

  componentDidMount() {
    const apiUrl = "http://127.0.0.1:5000/sendList/";
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) =>
        this.setState({
          rowData: data["data"],
        }),
      this.setState({loading:false}),
      );
  }

  fetchData(row) {
    const apiUrl = "http://127.0.0.1:5000/sendTxns/"+row;
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) =>
        this.setState({
          txns: data["txns"]
        })
      );
  }

  render() {
    return (
      <div>
          <span>
            <Table id="stocks" striped bordered hover variant="dark" style={{ cursor : "pointer", display:"inline-block", marginLeft:"10px",width: 600 }} size="sm">
              <tbody>
              <tr>
                <th>SYMBOL {this.state.loading}</th>
                <th>Net Value Acquired</th>
                <th>Net Qty Acquired</th>
                <th>Avg Buy Price</th>
                <th>LTP</th>
                <th>%diff</th>
              </tr>
              {this.state.rowData.map((item) => (
                <tr onClick={() => this.fetchData(item[0])}>
                  {item.map((val) => (
                    <td>{val}</td>
                  ))}
                </tr>
              ))}
              </tbody>
            </Table>
            <AdaptiveTable rowData={this.state.txns}/>
          </span>
      </div>
    );
  }
}
export default myComponent;
