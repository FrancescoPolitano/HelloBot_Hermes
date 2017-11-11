package com.grazianomarallo.RestfulService;

public abstract class Resource {
    private int capacity;
    private int busyLevel;
    private BaseInfo informations;

    public Resource(int capacity, BaseInfo informations) {
        this.capacity = capacity;
        this.busyLevel = 0;
        this.informations = informations;
    }

    public int getCapacity() {
        return capacity;
    }

    public void setCapacity(int capacity) {
        this.capacity = capacity;
    }

    public int getBusyLevel() {
        return busyLevel;
    }

    public void setBusyLevel(int busyLevel) {
        this.busyLevel = busyLevel;
    }

    public BaseInfo getInformations() {
        return informations;
    }

    public void setInformations(BaseInfo informations) {
        this.informations = informations;
    }
}
