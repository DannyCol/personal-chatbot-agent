export class CircularBuffer<T> {
    // a minimal circular buffer
    readonly maxSize: number;
    private data: T[];
    private pushIndex: number = 0;
    private _length: number = 0;
  
    constructor(maxSize: number) {
      this.data = new Array<T>(maxSize);
      this.maxSize = maxSize;
    }

    push(item: T) {
        this.data[this.pushIndex] = item;
        this.pushIndex = (this.pushIndex + 1) % this.maxSize;
        if (this._length < this.maxSize) {
            this._length++;
        }
    }

    [Symbol.iterator]() {
        let index = Math.abs((this.pushIndex - this._length) % this.maxSize);
        let itemsLeft = this._length;
        const data = this.data;
        const maxSize = this.maxSize;
        return {
            next(): IteratorResult<T> {
                if (itemsLeft === 0) {
                    return { value: undefined, done: true };
                }
                const value = data[index];
                index = (index + 1) % maxSize;
                itemsLeft--;
                return { value: value, done: false };
            }
        };
    }

    get length() {
        return this._length;
    }

    clear() {
        this._length = 0;
    }
};
