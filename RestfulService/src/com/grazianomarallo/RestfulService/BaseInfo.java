package com.grazianomarallo.RestfulService;


public class BaseInfo {
    private String name;
    private String address;
    private Coordinates coordinates;

    public BaseInfo(String name, String address, Coordinates coordinates) {
        this.name = name;
        this.address = address;
        this.coordinates = coordinates;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public Coordinates getCoordinates() {
        return coordinates;
    }

    public void setCoordinates(Coordinates coordinates) {
        this.coordinates = coordinates;
    }
}

